from pygtrie import CharTrie
from io import BytesIO
from tokenize import tokenize
from models.base import BaseModel

class TrieModel(BaseModel):
    finetune_implemented = True

    def __init__(self):
        super().__init__(name='trie_model')

    def predict(self, file, cursor_index, use_finetune=True):

        # check if model has been finetuned
        if use_finetune and self.finetuned:
            trie = self.ft_trie
        else:
            trie = CharTrie()

        # tokenise the incoming file into individual characters, store these into a trie
        for toknum, tokval, _, _, _ in tokenize(BytesIO(file.encode('utf-8')).readline):
            if tokval == 'utf-8' or toknum == 0: continue
            trie[tokval] = tokval

        # identify the prefix that the user is currently typing out
        prefix = file[:cursor_index:][::-1]
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

    def finetune(self, files):
        trie = CharTrie()

        # finetune trie on multiple files
        for toknum, tokval, _, _, _ in tokenize(BytesIO(files.encode('utf-8')).readline):
            if tokval == 'utf-8' or toknum == 0: continue
            trie[tokval] = tokval

        # set finetuned internally
        self.finetuned = True
        self.ft_trie = trie