import os
import requests
import json

from db.seeds.SBX5 import SBX5
from db.seeds.SBX4 import SBX4
from db.seeds.SBX3 import SBX3
from db.seeds.SBX2 import SBX2
from db.seeds.PROD import PROD

from src.services.token import Token

import azure.functions as func
import logging

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

tmp_directory = 'storage/tmp/'

@app.route(route="release-package/store")
def releasePackageStore(req: func.HttpRequest) -> func.HttpResponse:
    json_data = req.get_json()['releasePackage']
    logging.info(json_data)
    source_environment = json_data['sourceEnvironment']
    logging.info(source_environment)

    # environment = {}
    if source_environment == 'dev':
        logging.info('DEV-SBX5')
        environment = SBX5()
    elif source_environment == 'uat':
        logging.info('UAT-SBX4')
        environment = SBX4()
    elif source_environment == 'sit':
        logging.info('SIT-SBX2')
        environment = SBX2()
    elif source_environment == 'main':
        logging.info('PROD')
        environment = PROD()

    BITBUCKET_ENDPOINT = os.environ.get("BITBUCKET_ENDPOINT")
    BITBUCKET_REPOSITORY = os.environ.get("BITBUCKET_REPOSITORY")
    RAW_ENDPOINT = environment.bitbucket_raw

    files = json_data['pullRequestFiles']
    # those should be defined as azure env variables
    logging.info(BITBUCKET_ENDPOINT)
    logging.info(BITBUCKET_REPOSITORY)
    ################################################ 
    logging.info(RAW_ENDPOINT)
    logging.info(files)

    headers = {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36'}

    for file in files:   
        logging.info(file)

        url = BITBUCKET_ENDPOINT + BITBUCKET_REPOSITORY + RAW_ENDPOINT + file
        logging.info(url)
        response = requests.get(url, headers=headers)

        basename = os.path.basename(url)
        logging.info("BASENAME:")
        logging.info(basename)

        path = file.replace(basename, '')
        logging.info(path)

        if not os.path.exists(tmp_directory + path): 
            os.makedirs(tmp_directory + path)
        logging.info("DIR Created")
        
        logging.info(tmp_directory + path + basename)
        logging.info(response.content)

        try:
            with open(tmp_directory + path + basename, 'wb') as f:
                f.write(response.content)
            logging.info("File Written")
        except Exception as e:
            logging.error(f"Error writing file: {str(e)}")
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        
    try:
        return func.HttpResponse("Success", status_code=200)
    except ValueError as e:
        return func.HttpResponse(f"Errore: {str(e)}", status_code=400)

@app.route(route="release-package/deploy")
def releasePackageDeploy(req: func.HttpRequest) -> func.HttpResponse:
    try:
        return func.HttpResponse("Success", status_code=200)
    except ValueError as e:
        return func.HttpResponse(f"Errore: {str(e)}", status_code=400)