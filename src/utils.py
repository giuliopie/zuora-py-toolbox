import os
from azure.storage.blob import BlobServiceClient


storage_connection_string = os.environ["AzureWebJobsStorage"]
# Create BLOB Client Service
blob_service_client = BlobServiceClient.from_connection_string(storage_connection_string)
container_name = "testcicd"
# Get Container
container_client = blob_service_client.get_container_client(container_name)