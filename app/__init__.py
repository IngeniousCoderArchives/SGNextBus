from flask import Flask
from flask_uploads import UploadSet, configure_uploads

import logging
import modes
import os
import re


flaskapp = Flask(__name__)

mode = os.environ.get(modes.ENVIRONMENT_VARIABLE, modes.DEVELOPMENT)


import app.views

if __name__ == "__main__":
  flaskapp.run(host="0.0.0.0",port=80)
