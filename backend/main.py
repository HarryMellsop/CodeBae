from flask import Flask
from flask import request
from flask import jsonify

app = Flask(__name__)

from endpoints import ping
from endpoints import predict