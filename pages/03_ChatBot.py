import streamlit as st
import os
import time

from operator import itemgetter
from langchain_openai import AzureChatOpenAI
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_message_histories import CosmosDBChatMessageHistory
from langchain_core.runnables import ConfigurableFieldSpec

from common.utils import CustomAzureSearchRetriever
from common.prompts import WELCOME_MESSAGE, DOCSEARCH_PROMPT
from dotenv import load_dotenv
from uuid import uuid4

load_dotenv()

# SETUP
AZURE_OPENAI_MODEL_NAME = os.environ.get("AZURE_OPENAI_MODEL_NAME")
os.environ["OPENAI_API_VERSION"] = os.environ.get("AZURE_OPENAI_API_VERSION")

def get_session_history(session_id, user_id):
    cosmos = CosmosDBChatMessageHistory(
        cosmos_endpoint=os.environ['AZURE_COSMOSDB_ENDPOINT'],
        cosmos_database=os.environ['AZURE_COSMOS_DATABASE_NAME'],
        cosmos_container=os.environ['AZURE_COSMOSDB_CONTAINER_NAME'],
        connection_string=os.environ['AZURE_COMOSDB_CONNECTION_STRING'],
        session_id=session_id,
        user_id=user_id
    )
    cosmos.prepare_cosmos()
    return cosmos

st.title("Noventiq Smartbot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid4())

if "user_id" not in st.session_state:
    st.session_state.user_id = "web" + str(int(time.time()))

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        llm = AzureChatOpenAI(deployment_name=AZURE_OPENAI_MODEL_NAME, 
                              temperature=0, 
                              max_tokens=1500, 
                              streaming=True)

        retriever = CustomAzureSearchRetriever(
            indexes=[os.environ['AZURE_SEARCH_INDEX']], 
            topK=20, 
            reranker_threshold=1, 
            sas_token=os.environ['BLOB_SAS_TOKEN']
        )

        chain = (
            {
                "context": itemgetter("question") | retriever, 
                "question": itemgetter("question"), 
                "history": itemgetter("history")
            } 
                | DOCSEARCH_PROMPT 
                | llm
            )
        
        chain_with_history = RunnableWithMessageHistory(
            chain,
            get_session_history,
            input_messages_key="question",
            history_messages_key="history",
            history_factory_config=[
                ConfigurableFieldSpec(
                    id="user_id",
                    annotation=str,
                    name="User ID",
                    description="Unique identifier for the user.",
                    default="",
                    is_shared=True,
                ),
                ConfigurableFieldSpec(
                    id="session_id",
                    annotation=str,
                    name="Session ID",
                    description="Unique identifier for the conversation.",
                    default="",
                    is_shared=True,
                ),
            ],
        ) | StrOutputParser()

        config={"configurable": {"session_id": st.session_state.session_id, "user_id": st.session_state.user_id}}

        response = st.write_stream(chain_with_history.stream({"question": prompt}, config=config))
    st.session_state.messages.append({"role": "assistant", "content": response})