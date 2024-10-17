import streamlit as st
import os
import time

from operator import itemgetter
from langchain_openai import AzureChatOpenAI
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_message_histories import CosmosDBChatMessageHistory
from langchain_core.runnables import ConfigurableFieldSpec
from langchain.tools.retriever import create_retriever_tool
from langchain.agents import AgentExecutor, create_openai_tools_agent


from common.utils import CustomAzureSearchRetriever, CustomBingRetriever, parse_citation
from common.prompts import WELCOME_MESSAGE, DOCSEARCH_PROMPT, AGENT_DOCSEARCH_PROMPT
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

llm = AzureChatOpenAI(deployment_name=AZURE_OPENAI_MODEL_NAME, 
                      temperature=0, 
                      max_tokens=1500, 
                      streaming=True)

retriever = CustomBingRetriever(topK=5)

retriever_tool = create_retriever_tool(
            retriever,
            "bing_search",
            "Search for information about everything. If users want to retrieve any information, e.g: time, weather, general knowledge, etc. you must use this tool"
        )

tools = [retriever_tool]
prompt = AGENT_DOCSEARCH_PROMPT

agent = create_openai_tools_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False)

chain_with_history = RunnableWithMessageHistory(
    agent_executor,
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
)

st.markdown(
    """
<style>
    .st-emotion-cache-1c7y2kd {
        width: 50%;
        margin-left: auto;
        align-self: flex-end;
        text-align: left;
        box-shadow: 0 6px 12px 0 rgba(0, 0, 0, 0.3);
    }
    .st-emotion-cache-bho8sy {
        background-image: url("https://global.kyocera.com/favicon.ico")
    }
    .st-emotion-cache-1ghhuty {
        display: none;
        visibility: hidden;
    }
    .st-emotion-cache-1pbsqtx {
        display: none;
        visibility: hidden;
    }
</style>
""",
    unsafe_allow_html=True,
)


st.title("Noventiq Smartbot")

# Initialize chat history
if "bing_session_id" not in st.session_state:
    st.session_state.session_id = str(uuid4())

if "user_id" not in st.session_state:
    st.session_state.user_id = "bingchat" + str(int(time.time()))

if "bing_messages" not in st.session_state:
    st.session_state.bing_messages = []

# Display chat messages from history on app rerun
for message in st.session_state.bing_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.bing_messages.append({"role": "user", "content": prompt})

    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):

        # chain = (
        #     {
        #         "context": itemgetter("question") | retriever, 
        #         "question": itemgetter("question"), 
        #         "history": itemgetter("history")
        #     } 
        #         | DOCSEARCH_PROMPT 
        #         | llm
        #     )

        config={"configurable": {"session_id": st.session_state.session_id, "user_id": st.session_state.user_id}}

        with st.empty():
            st.write("Searching...")
            start = time.time()
            response = chain_with_history.invoke({"question": prompt}, config=config)["output"]
            response = "\n\n" + response + parse_citation(response, True)
            st.write(f"Responded in {int(time.time() - start)}s" + response)

    st.session_state.bing_messages.append({"role": "assistant", "content": response})
