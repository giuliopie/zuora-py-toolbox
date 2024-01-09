from src import app
from flask import request
from urllib.request import urlretrieve
import os
import requests
import json



@app.route('/api/deploy', methods=['POST'])
def deploy():
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
        
        if not os.path.exists("storage/tmp/"+ path): 
            os.makedirs("storage/tmp/"+ path)
            
        with open('storage/tmp/' + path + '/' + basename, 'wb') as f:
            f.write(response.content)

    return 200