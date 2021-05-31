from flask import request
from utils.error import GenericError
from utils.session_validation import validate_session
import json

from main import app
from main import session_cache
from main import user_db
from main import s3bucket


@app.route('/mass_upload', methods=['POST'])
def mass_upload():

    # verify session ID
    session_id = request.headers.get('Session-ID')
    user_data = validate_session(session_id)

    # decode request data
    try:
        data = json.loads(request.data.decode('utf8'))
    except ValueError:
        raise GenericError('Error: Unable to decode request data payload; check that your payload exists and is well-formed JSON', 400)

    # check for workspace
    if 'workspace' not in data:
        raise GenericError('Error: Parameter \'workspace\' not found in the request body.  You must provide this parameter to this endpoint.', 400)

    # check for files
    if 'files' not in data:
        raise GenericError('Error: Parameter \'files\' not found in the request body.  You must provide this parameter to this endpoint.', 400)

    # save uploaded files in s3
    for path in data['files']:
        s3bucket.save_file(data['workspace'], user_data, data['files'][path], path)
    
    return "Successfully uploaded files to the bucket."