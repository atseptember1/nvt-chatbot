import streamlit as st
import os

from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient, BlobClient, ContentSettings
load_dotenv()

BLOB_URL = os.environ.get("BLOB_URL")
BLOB_ADMIN_TOKEN = os.environ.get("BLOB_ADMIN_TOKEN")
BLOB_CONTAINER_NAME = os.environ.get("BLOB_CONTAINER_NAME")


blob_service_client = BlobServiceClient(BLOB_URL, credential=BLOB_ADMIN_TOKEN)
container_client = blob_service_client.get_container_client(container=BLOB_CONTAINER_NAME)
content_settings = ContentSettings(content_type='application/pdf')

st.set_page_config(page_title="Noventiq Smart Bot", page_icon="📖", layout="wide")

st.header("Noventiq Smart Bot")

# uploaded_files = st.file_uploader("Choose documents", type=["pdf"], accept_multiple_files=True)
# for uploaded_file in uploaded_files:
#     bytes_data = uploaded_file.read()
#     blob_client = container_client.upload_blob(name=uploaded_file.name, data=bytes_data, overwrite=True, content_settings=content_settings)