from flask import request
from utils.error import GenericError

from main import app
from main import model
from main import session_cache
from main import user_db

@app.route('/mass_upload', methods=['POST'])
def mass_upload():

    # ensure that the user has a valid session ID
    session_id = request.headers.get('Session-ID')
    validate_session(session_id)