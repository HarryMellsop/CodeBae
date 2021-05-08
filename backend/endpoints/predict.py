from flask import request
from utils.error import GenericError
from utils.session_validation import validate_session

from main import app
from main import model
from main import session_cache

@app.route('/predict', methods=['POST'])
def predict():

    # ensure that the user has a valid session ID
    validate_session(request.headers.get('Session-ID'))

    # get input data
    data = request.form
    if 'current_file' not in data:
        raise GenericError('Error: You must provide the current file parameter when using this endpoint', 400)

    # validate input format
    index = data['current_file'].find('<cursor>')
    if index == -1:
        raise GenericError('Error: Parameter \'current_file\' does not contain <cursor>', 400)

    return model.predict(data['current_file'], index)