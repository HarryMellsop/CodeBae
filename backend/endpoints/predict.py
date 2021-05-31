from flask import request, jsonify
from utils.error import GenericError
from utils.session_validation import validate_session

from main import app
from main import s3bucket
from main import session_cache
from main import USER_SESSION_MODEL_TTL

from main import model_kwargs
from main import model_class
from main import default_model


@app.route('/predict', methods=['POST'])
def predict():

    # verify session
    session_id = request.headers.get('Session-ID')
    user_data = validate_session(session_id)

    # get input file
    data = request.form
    if 'current_file' not in data:
        raise GenericError('Error: You must provide the current file parameter when using this endpoint', 400)

    # validate input file
    index = data['current_file'].find('<cursor>')
    if index == -1:
        raise GenericError('Error: Parameter \'current_file\' does not contain <cursor>', 400)

    # if the model we're using is capable of finetuning, let's try it
    if model_class.finetune_implemented:

        # chech for serialized finetuned model
        model_serial = session_cache.get(session_id + '.model.ft')

        # no user-specific model found, let's try to finetune one on user data
        if model_serial is None:

            # get user files
            user_files = s3bucket.get_files(user_data)

            # finetune model on user data
            model = model_class(**model_kwargs)
            model.finetune(' '.join(user_files))
            model_serial = model_class.save(model)

            # save model in session cache
            session_cache.set(session_id + '.model.ft', model_serial, timeout=USER_SESSION_MODEL_TTL)
            
        # found a model for the users, let's load it
        else:
            model = model_class.load(model_serial)
    
    # if the model can't finetune, let's just use the already-existing default model
    else:
        model = default_model

    predictions = model.predict(data['current_file'], index)
    return jsonify({'predictions' : predictions})