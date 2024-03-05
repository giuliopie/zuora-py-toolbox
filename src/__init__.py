from flask import Flask
from src.config.config import Config
from dotenv import load_dotenv

# loading environment variables
load_dotenv()

# declaring flask application
app = Flask(__name__)

# calling the dev configuration
config = Config().dev_config

# making our application to use dev env
app.env = config.ENV

if __name__ == '__main__':
    app.debug = True
    app.run()