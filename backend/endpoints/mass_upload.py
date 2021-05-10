from flask import request
from utils.error import GenericError
from utils.session_validation import validate_session
import json

from main import app
from main import model
from main import session_cache
from main import user_db
from main import s3bucket

@app.route('/mass_upload', methods=['POST'])
def mass_upload():

    # ensure that the user has a valid session ID
    session_id = request.headers.get('Session-ID')
    validate_session(session_id)

    # get the user_data object from the cache
    user_data = session_cache.get(session_id)
    if user_data == None:
        raise GenericError('Internal Error finding relevant user data from session_id - has your session expired?', 419)

    try:
        data = json.loads(request.data.decode('utf8'))
    except ValueError:
        raise GenericError('Error: Unable to decode request data payload; check that your payload exists and is well-formed JSON', 400)

    if 'workspace' not in data:
        raise GenericError('Error: Parameter \'workspace\' not found in the request body.  You must provide this parameter to this endpoint.', 400)

    if 'files' not in data:
        raise GenericError('Error: Parameter \'files\' not found in the request body.  You must provide this parameter to this endpoint.', 400)

    for path in data['files']:
        s3bucket.save_file(data['workspace'], user_data, data['files'][path], path)
    
    return "Successfully uploaded files to the bucket."