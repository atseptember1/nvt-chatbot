import streamlit as st
import pandas as pd
import os
from azure.cosmos import CosmosClient, PartitionKey
from dotenv import load_dotenv

load_dotenv()


AZURE_COSMOS_ENDPOINT = os.environ.get("AZURE_COSMOSDB_ENDPOINT")
AZURE_COSMOS_DATABASE_NAME = os.environ.get("AZURE_COSMOS_DATABASE_NAME")
AZURE_COMOSDB_CONNECTION_STRING = os.environ.get("AZURE_COMOSDB_CONNECTION_STRING")
AZURE_COSMOS_CONTAINER_NAME = "document-log"

client = CosmosClient.from_connection_string(AZURE_COMOSDB_CONNECTION_STRING)
db = client.create_database_if_not_exists(id=AZURE_COSMOS_DATABASE_NAME)
container = db.create_container_if_not_exists(id=AZURE_COSMOS_CONTAINER_NAME,
                                              partition_key=PartitionKey("/id"))

st.set_page_config(page_title="Documents",layout='wide')
st.header("Documents")

try: 
    item_list = list(container.read_all_items(max_item_count=10))

    documents = []
    for doc in item_list:
        tmp = {
            "ID": doc["id"],
            "Name": doc["document_name"],
            "Location": doc["document_url"],
            "Pages": doc["pages"],
            "Status": doc["status"],
            "Error": doc["error"],
            "Updated_at": doc["updated_at"]
        }
        documents.append(tmp)

    df = pd.DataFrame(documents)

    st.dataframe(
        df,
        column_config={
            "ID": st.column_config.TextColumn(label="ID", width="small"),
            "Name": st.column_config.TextColumn(label="Name", width="large"),
            "Location": st.column_config.LinkColumn("Location", width="large"),
            "Pages": st.column_config.NumberColumn(label="Pages", width="small"),
            "Status": st.column_config.TextColumn(label="Status", width="small"),
            "Error": st.column_config.TextColumn(label="Error", width="small"),
            "Updated_at": st.column_config.DatetimeColumn(label="Updated_at", width="medium")
        },
        hide_index=True
    )
except Exception as e:
    st.write("Please upload a document then come back here to check its status")