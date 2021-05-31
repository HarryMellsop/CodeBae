from werkzeug.exceptions import HTTPException 
from flask import jsonify

from main import app


@app.errorhandler(HTTPException)
def handle_invalid_usage(error):

    # return generic error format
    return {
        'description': error.description,
        'code': error.code 
    }