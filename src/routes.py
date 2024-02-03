from src import app
from flask import request
from urllib.request import urlretrieve
import os
import requests
import json

from db.seeds.SBX4 import SBX4
from db.seeds.SBX5 import SBX5

from src.services.token import Token
from src.utils import Utils
from src.controllers.workflow import WorkflowController as Workflow

tmp_directory = 'storage/tmp/'

@app.route('/api/release-package/store', methods=['POST'])
def storeReleasePackage():
    json_data = request.get_json()

    BITBUCKET_ENDPOINT = os.environ.get("BITBUCKET_ENDPOINT")
    BITBUCKET_REPOSITORY = os.environ.get("BITBUCKET_REPOSITORY")
    RAW_ENDPOINT = os.environ.get("RAW_ENDPOINT")

    files = json_data['pullRequestFiles']
    headers = {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36'}

    for file in files:    
        url = BITBUCKET_ENDPOINT + BITBUCKET_REPOSITORY + RAW_ENDPOINT + file
    
        response = requests.get(url, headers=headers)

        basename = os.path.basename(url)
        path = file.replace(basename, '')
        
        if not os.path.exists(tmp_directory + path): 
            os.makedirs(tmp_directory + path)
            
        with open(tmp_directory + path + '/' + basename, 'wb') as f:
            f.write(response.content)
    return "200"

@app.route('/api/release-package/deploy', methods=["POST"])
def deployReleasePackage():
    module = 'workflows'

    target_environment = request.get_json()['targetEnvironment']

    if target_environment == 'dev':
            print('DEV-SBX5')
            environment = SBX5()
    elif target_environment == 'uat':
            print('UAT-SBX4')
            environment = SBX4()
    elif target_environment == 'sit':
            print('SIT-SBX2')
    elif target_environment == 'main':
            print('PROD')
    
    token = Token(environment.client_id, environment.client_secret)
    bearer_token = token.get_access_token()

    wf = Workflow()
    wf_list = wf.getWorkflowFromTargetEnvironment()
    
    workflow_files = os.listdir(tmp_directory + module)

    for workflow in workflow_files:
        result = next((obj for obj in wf_list if obj['name'] == workflow.replace('.json', '')), None)
        file_path = tmp_directory + module + '/' + workflow
        wf_version = str(json.load(open(file_path, 'r'))['workflow']['version'])

    if result != None:
        wf_id = str(result['id'])
        wf.importNewWorflowVersionToTargetEnvironment(bearer_token, wf_id, wf_version, file_path)
    else:
        wf.importNewWorflowToTargetEnvironment(bearer_token, wf_version, file_path)

    return "200"

    

