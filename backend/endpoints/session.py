from flask import request
from utils.error import GenericError
import uuid

from main import app
from main import user_db
from main import session_cache
from main import USER_SESSION_TTL


@app.route('/session', methods=['GET'])
def session():

    # check for api keys
    api_key = request.headers.get('API-Key')
    if api_key is None:
        raise GenericError('Error: Must provide API-Key header in request.', 400)

    # validate api key
    user_data = user_db.get_user(api_key=api_key)
    if user_data is None: 
        raise GenericError('Error: Invalid API key.', 403)

    # generate new session
    session_id = str(uuid.uuid4().hex)
    session_cache.set(session_id, user_data, timeout=USER_SESSION_TTL)
    return session_id