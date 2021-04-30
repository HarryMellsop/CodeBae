from flask import jsonify
from main import app
from utils.error import GenericError

@app.errorhandler(GenericError)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response