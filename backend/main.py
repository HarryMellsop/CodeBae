from flask import Flask
from flask import request
from flask import jsonify

# Define the application logic (all in one file, until we expand functionality and factor later)

app = Flask(__name__)

@app.route('/ping')
def ping_endpoint():
    return 'pong'

@app.route('/predict', methods = ['POST'])
def predict():
    data = request.form

    # we expect the payload of the request to contain the parameter 'current_file' with the current cursor position delineated
    # by <cursor> (just for now, we should ultimately do something more thoughtful)
    if 'current_file' not in data:
        raise GenericError("Error: You must provide the current file parameter when using this endpoint", status_code=422)

    index = data['current_file'].find('<cursor>')
    if index == -1:
        raise GenericError("Error: Parameter 'current_file' does not contain <cursor>")

    if index > 0:
        return 'The character before your cursor is a ' + data['current_file'][index - 1] + ', I see!'
    else:
        return 'There is no character before your cursor; that makes things quite hard to predict'

# Very basic error handling functionality

class GenericError(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

@app.errorhandler(GenericError)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

