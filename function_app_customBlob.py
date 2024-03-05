import os
from azure.storage.blob import BlockBlobService

account_name = "mendixzuoracicd"
container_name = "zuora-release-packages"
blob_name = "nome_del_blob"
file_path = "percorso_del_tuo_file_csv_locale"

account_key = os.environ.get("AZURE_STORAGE_ACCOUNT_KEY")
# Creare un'istanza di BlockBlobService
block_blob_service = BlockBlobService(account_name=account_name, account_key=account_key)

# Converti il dizionario JSON in una stringa JSON
json_string = json.dumps(json_data)

# Crea un blob dal JSON e caricalo nel contenitore
block_blob_service.create_blob_from_text(container_name, blob_name, json_string)

print(f"Il file JSON è stato caricato correttamente come {blob_name} nel contenitore {container_name}.")

