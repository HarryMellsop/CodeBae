from flask import request
from utils.error import GenericError

from main import app
from main import session_cache

def validate_session(session_id):
    if session_id is None: 
        raise GenericError('Error: Must provide Session-ID header in request.', 400)
    
    # validate session id
    user_data = session_cache.get(session_id)
    if user_data is None: 
        raise GenericError('Error: Invalid session ID.', 403)