from flask import Flask
from flask import request
from flask import jsonify
from models.trie import TrieModel
from models.transformer.transformer import TransformerModel
from utils.db import UserDatabase
from utils.cache import SessionCache

# start app
app = Flask(__name__)

# init global constants
USER_SESSION_TTL = 1 * 60 * 60

# init global variables
model = TransformerModel(param_path='./models/transformer/ckpts/training_checkpoints/epoch_0_iter_85000.pt')
user_db = UserDatabase()
session_cache = SessionCache(app)

# add endpoints
from endpoints import error
from endpoints import ping
from endpoints import session
from endpoints import predict
