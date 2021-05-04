from flask import Flask
from flask import request
from flask import jsonify

# Define the application logic (all in one file, until we expand functionality and factor later)

app = Flask(__name__)

@app.route('/ping')
def ping_endpoint():
    return 'pong'

# import the relevant prediction endpoints
import prediction