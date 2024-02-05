import os
import requests
import json

class WorkflowController:

    api_path = os.environ.get("Z_SANDBOX_BASE_URL") + 'workflows'
    api_path_import = '/import'
    api_path_import_version = '/{workflow_id}/versions/import'
    
    def getWorkflowFromTargetEnvironment(self, bearer_token):
        workflow_list = []
        page_counter = 1

        while True:
            workflows = requests.get(
                self.api_path,
                params = {
                    'page': str(page_counter),
                    'page_length': '50'
                },
                headers = {
                    'Content-Type': 'application/json; charset=utf-8',
                    'Authorization': 'Bearer ' + bearer_token
                }
            )
            page_counter = page_counter + 1
            
            for workflow in workflows.json()['data']:
                item = {
                    'id': workflow['id'],
                    'name': workflow['name'].replace(' ', '')
                }
                workflow_list.append(item)    

            if 'next_page' not in workflows.json()['pagination']:
                break

        return workflow_list

    def importNewWorflowVersionToTargetEnvironment(self, bearer_token, workflow_id, version, file_path):
        with open(file_path, 'r') as file:
            json_data = json.load(file)

        url = self.api_path + self.api_path_import_version.replace('{workflow_id}', workflow_id)

        response = requests.post(
            url,
            json=json_data,
            params = {
                "activate": 'true',
                "version": version
            },
            headers= {
                'Accept-Encoding': 'gzip, deflate',
                'Accept': 'application/json; charset=utf-8',
                'Content-Type': 'application/json; charset=utf-8',
                'Authorization': 'Bearer ' + bearer_token
            }
        )

        return response.json()
    
    def importNewWorflowToTargetEnvironment(self, bearer_token, version, file_path):
        with open(file_path, 'r') as file:
            json_data = json.load(file)

        url = self.api_path + self.api_path_import

        response = requests.post(
            url,
            json=json_data,
            params = {
                "activate": 'true',
                "version": version
            },
            headers= {
                'Accept-Encoding': 'gzip, deflate',
                'Accept': 'application/json; charset=utf-8',
                'Content-Type': 'application/json; charset=utf-8',
                'Authorization': 'Bearer ' + bearer_token
            }
        )

        return response.json()


