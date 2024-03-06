import os
import requests

class Token:
    
    RESOURCE_PATH = 'oauth/token'

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret

    def __set_bearer_token(self):
        api_url = os.environ.get("Z_SANDBOX_BASE_URL") + self.RESOURCE_PATH
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials"
        }
        form_response = requests.post(
            api_url,
            data=data,
            headers= {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        )
        json_data = form_response.json()

        access_token = json_data.get('access_token')

        if access_token is not None:
            return access_token
        else:
            return None

    def get_access_token(self):
        return self.__set_bearer_token()