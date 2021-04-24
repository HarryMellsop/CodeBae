from main import app
from flask import request
from error import GenericError
from tokenize import tokenize
from io import BytesIO
from pygtrie import CharTrie

@app.route('/predict', methods = ['POST'])
def predict():
    data = request.form
    # req<cursor>

    # we expect the payload of the request to contain the parameter 'current_file' with the current cursor position delineated
    # by <cursor> (just for now, we should ultimately do something more thoughtful)
    if 'current_file' not in data:
        raise GenericError('Error: You must provide the current file parameter when using this endpoint', status_code=422)

    index = data['current_file'].find('<cursor>')
    if index == -1:
        raise GenericError('Error: Parameter \'current_file\' does not contain <cursor>')

    return get_prediction_naive(data['current_file'], index)

# implements the most naive prediction scheme
def get_prediction_naive(file, cursor_index):
    # tokenise the incoming file into individual characters, store these into a trie
    trie = CharTrie()
    for toknum, tokval, _, _, _ in tokenize(BytesIO(file.encode('utf-8')).readline):
        trie[tokval] = tokval
    
    # identify the prefix that the user is currently typing out
    prefix = file[0:cursor_index:]
    prefix = prefix[::-1]
    
    terminating = len(prefix) - 1
    for i in range(len(prefix)):
        if not prefix[i].isalpha() and prefix[i] != '_':
            terminating = i
            break

    prefix = prefix[:terminating]
    prefix = prefix[::-1]

    # ensure that we don't predict what the user is already typing...
    del trie[prefix]

    try:
        return list(trie.values(prefix))[0]
    except KeyError:
        # no predictions
        return ''

    return file