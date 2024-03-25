import os
import requests
import json

from db.seeds.SBX5 import SBX5
from db.seeds.SBX4 import SBX4
from db.seeds.SBX2 import SBX2
from db.seeds.PROD import PROD

from src.services.token import Token
from src.controllers.workflow import WorkflowController as Workflow

import azure.functions as func
import logging

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

from src.utils import container_client

def getEnvironment(environment):
    if environment == 'dev':
        logging.info('DEV-SBX5')
        environment = SBX5()
    elif environment == 'uat':
        logging.info('UAT-SBX4')
        environment = SBX4()
    elif environment == 'sit':
        logging.info('SIT-SBX2')
        environment = SBX2()
    elif environment == 'main':
        logging.info('PROD')
        environment = PROD()
    return environment

@app.route(route="release-package/store")
def releasePackageStore(req: func.HttpRequest) -> func.HttpResponse:
    json_data = req.get_json()['releasePackage']
    source_environment = json_data['sourceEnvironment']

    environment = getEnvironment(source_environment)

    BITBUCKET_ENDPOINT = os.environ.get("BITBUCKET_ENDPOINT")
    BITBUCKET_REPOSITORY = os.environ.get("BITBUCKET_REPOSITORY")
    RAW_ENDPOINT = environment.bitbucket_raw

    files = json_data['pullRequestFiles']

    headers = {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36'}

    for file in files:
        url = BITBUCKET_ENDPOINT + BITBUCKET_REPOSITORY + RAW_ENDPOINT + file
        response = requests.get(url, headers=headers)
        json_content = response.json()

        blob_name = file
        # Create BLOB
        blob_client = container_client.get_blob_client(blob_name)
        blob_client.upload_blob(json.dumps(json_content), overwrite=True)

    try:
        return func.HttpResponse("Success", status_code=200)
    except ValueError as e:
        return func.HttpResponse(f"Errore: {str(e)}", status_code=400)

@app.route(route="release-package/deploy")
def releasePackageDeploy(req: func.HttpRequest) -> func.HttpResponse:
    # Set here the allowed module for deploy as array
    module = 'workflows'

    req_body = req.get_json()
    target_environment = req_body.get('targetEnvironment')

    environment = getEnvironment(target_environment)

    token = Token(environment.client_id, environment.client_secret)
    bearer_token = token.get_access_token()

    wf = Workflow()
    wf_list = wf.getWorkflowFromTargetEnvironment(bearer_token)

    # Get all blobs with the starting prefix
    blobs = container_client.walk_blobs(name_starts_with= module + '/' )

    for blob in blobs:
        file_path = blob.name

        workflow = file_path.replace('.json', '')
        workflow = workflow.replace('workflows/', '')

        result = next((obj for obj in wf_list if obj['name'] == workflow), None)

        blob_client = container_client.get_blob_client(file_path)
        blob_content = blob_client.download_blob().readall()

        wf_version = str(json.loads(blob_content)['workflow']['version'])

        if result != None:
            wf_id = str(result['id'])
            logging.info('true')
            wf.importNewWorflowVersionToTargetEnvironment(bearer_token, wf_id, wf_version, file_path)
        else:
            logging.info('false')
            wf.importNewWorflowToTargetEnvironment(bearer_token, wf_version, file_path)

    try:
        return func.HttpResponse("Success", status_code=200)
    except ValueError as e:
        return func.HttpResponse(f"Errore: {str(e)}", status_code=400)

@app.route(route="refresh/standard/objects")
def refreshStandardObjects(req: func.HttpRequest) -> func.HttpResponse:

    req_body = req.get_json()
    target_environment = req_body.get('targetEnvironment')

    environment = getEnvironment(target_environment)

    token = Token(environment.client_id, environment.client_secret)
    bearer_token = token.get_access_token()

    actionQueryPayload = {
        "queryString": "SELECT Id FROM Account"
    }

    url = environment.base_endpoint + 'v1/action/query'
    accounts = requests.post(
        url,
        json = actionQueryPayload,
        headers = {
            'Accept-Encoding': 'gzip, deflate',
            'Accept': 'application/json; charset=utf-8',
            'Content-Type': 'application/json; charset=utf-8',
            'Authorization': 'Bearer ' + bearer_token
        }
    )

    accounts = json.loads(accounts.content).get('records')
    for account in accounts:
        url = environment.base_endpoint + 'v1/accounts/' + account.get('Id')
        requests.delete(
            url,
            headers = {
                'Accept-Encoding': 'gzip, deflate',
                'Accept': 'application/json; charset=utf-8',
                'Content-Type': 'application/json; charset=utf-8',
                'Authorization': 'Bearer ' + bearer_token
            }
        )

    try:
        return func.HttpResponse("Success", status_code=200)
    except ValueError as e:
        return func.HttpResponse(f"Errore: {str(e)}", status_code=400)
    
@app.route(route="refresh/productcatalog")
def refreshProductCatalog(req: func.HttpRequest) -> func.HttpResponse:

    req_body = req.get_json()
    target_environment = req_body.get('targetEnvironment')

    environment = getEnvironment(target_environment)

    token = Token(environment.client_id, environment.client_secret)
    bearer_token = token.get_access_token()


    page_counter = 1
    while True:
        url = environment.base_endpoint + 'v1/catalog/products'
        
        productCatalogResponse = requests.get(
            url,
            params = {
                'page': str(page_counter),
                'page_length': '40'
            },
            headers= {
                'Accept-Encoding': 'gzip, deflate',
                'Accept': 'application/json; charset=utf-8',
                'Content-Type': 'application/json; charset=utf-8',
                'Authorization': 'Bearer ' + bearer_token
            }
        )
        page_counter = page_counter + 1

        productCatalog = json.loads(productCatalogResponse.content).get('products')
        for product in productCatalog:
            url = environment.base_endpoint + 'v1/object/product/' + product.get('id')
            requests.delete(
                url,
                headers= {
                    'Accept-Encoding': 'gzip, deflate',
                    'Accept': 'application/json; charset=utf-8',
                    'Content-Type': 'application/json; charset=utf-8',
                    'Authorization': 'Bearer ' + bearer_token
                }
            )  
        if 'nextPage' not in json.loads(productCatalogResponse.content).keys():
            break

    try:
        return func.HttpResponse("Success", status_code=200)
    except ValueError as e:
        return func.HttpResponse(f"Errore: {str(e)}", status_code=400)
