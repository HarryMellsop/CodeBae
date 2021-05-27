from flask import request, jsonify
from utils.error import GenericError
from utils.session_validation import validate_session

from main import app
from main import model_class
from main import s3bucket
from main import session_cache
from main import USER_SESSION_MODEL_TTL

model = model_class(param_path='./models/transformer_params.pt')

@app.route('/predict', methods=['POST'])
def predict():

    # ensure that the user has a valid session ID
    session_id = request.headers.get('Session-ID')
    user_data = validate_session(session_id)

    # get input data
    data = request.form
    if 'current_file' not in data:
        raise GenericError('Error: You must provide the current file parameter when using this endpoint', 400)

    # validate input format
    index = data['current_file'].find('<cursor>')
    if index == -1:
        raise GenericError('Error: Parameter \'current_file\' does not contain <cursor>', 400)

    # # chech for serialized finetuned model
    # model_serial = session_cache.get(session_id + '.model.ft')
    # if model_serial is None:

    #     # get user files
    #     files = s3bucket.get_files(user_data)

    #     # finetune model
    #     model = model_class(param_path='./models/transformer_params.pt')
    #     # model.finetune(' '.join(files))
    #     model_serial = model_class.save(model)

    #     # save model in session cache
    #     session_cache.set(session_id + '.model.ft', model_serial, timeout=USER_SESSION_MODEL_TTL)
    
    # else:
    #     model = model_class.load(model_serial)
    
    predictions = model.predict(data['current_file'], index)
    return jsonify({'predictions' : predictions})