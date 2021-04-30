from flask import request
from error import GenericError
from main import app
from models.trie import TrieModel

@app.route('/predict', methods=['POST'])
def predict():
    data = request.form

    # we expect the payload of the request to contain the parameter 'current_file' with the current cursor position delineated
    # by <cursor> (just for now, we should ultimately do something more thoughtful)
    if 'current_file' not in data:
        raise GenericError('Error: You must provide the current file parameter when using this endpoint', status_code=422)

    index = data['current_file'].find('<cursor>')
    if index == -1:
        raise GenericError('Error: Parameter \'current_file\' does not contain <cursor>')

    trie_model = TrieModel()
    return trie_model.predict(data['current_file'], index)