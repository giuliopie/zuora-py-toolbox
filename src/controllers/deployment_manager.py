import os
import requests

class DeploymentManagerController:

    def __init__(self):
        self.target_environment = target_environment
        self.source_environment = source_environment

    def executeDeploy(self)