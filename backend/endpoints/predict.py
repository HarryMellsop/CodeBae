from flask import request, jsonify
from utils.error import GenericError

from main import app
from main import model
from main import session_cache

@app.route('/predict', methods=['POST'])
def predict():

    # check for session id
    session_id = request.headers.get('Session-ID')
    if session_id is None: 
        raise GenericError('Error: Must provide Session-ID header in request.', 400)
    
    # validate session id
    user_data = session_cache.get(session_id)
    if user_data is None: 
        raise GenericError('Error: Invalid session ID.', 403)

    # get input data
    data = request.form
    if 'current_file' not in data:
        raise GenericError('Error: You must provide the current file parameter when using this endpoint', 400)

    # validate input format
    index = data['current_file'].find('<cursor>')
    if index == -1:
        raise GenericError('Error: Parameter \'current_file\' does not contain <cursor>', 400)

    predictions = model.predict(data['current_file'], index)
    return jsonify({'predictions' : predictions})