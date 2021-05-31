from flask import Flask
from flask import request
from flask import jsonify
from models.trie import TrieModel
from models.transformer.transformer import TransformerModel
from utils.db import UserDatabase
from utils.bucket import S3Bucket
from utils.cache import SessionCache
from utils.extract_credentials import extract_aws_credentials

# start app
app = Flask(__name__)

# init global constants
USER_SESSION_TTL = 1 * 60 * 60
USER_SESSION_MODEL_TTL = 24 * 60 * 60

# init model/class
model_kwargs = {'param_path': './models/params/transformer_params.pt'}
model_class = TransformerModel
default_model = model_class(**model_kwargs)

# init aws resources
credentials = extract_aws_credentials()
user_db = UserDatabase(credentials=credentials)
s3bucket = S3Bucket(credentials=credentials)

# init session cache
session_cache = SessionCache(app)

# add endpoints
from endpoints import error
from endpoints import ping
from endpoints import session
from endpoints import predict
from endpoints import mass_upload
