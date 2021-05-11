from pygtrie import CharTrie
from io import BytesIO
from tokenize import tokenize
from models.base import BaseModel

class TrieModel(BaseModel):

    def __init__(self):
        super().__init__(name='trie_model')

    def predict(self, file, cursor_index):

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
            return list(trie.values(prefix))[:3]
        except KeyError:
            # no predictions
            return []