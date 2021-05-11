import nltk
nltk.download('punkt')
from collections import defaultdict
from nltk.tokenize import word_tokenize
from pygtrie import CharTrie
from io import BytesIO
from tokenize import tokenize
from models.base import BaseModel

class comboModel(BaseModel):
    def __init__(self):
        super().__init__(name='combo_model')

    def predict(self, file, cursor_index):
        ngramToCount = defaultdict(float)
        wordCount = defaultdict(float)
        vocabSet = set()
        useMLE = False

        #get previous word
        prefix = file[0:cursor_index:]
        prefix = prefix[::-1]
        terminating = len(prefix)

        #decide whether to use mle or trie
        #if not either of these cases, use Trie as default
        if prefix[0] == ' ':
            prefix = prefix[1:]
            useMLE = True
        elif not prefix[0].isalpha() and prefix[0] != '_' and prefix[0] != '.':
            prefix = prefix[:1]
            useMLE = True
         for i in range(len(prefix)):
            if not prefix[i].isalpha() and prefix[i] != '_' and prefix[i] != '(' and prefix[i] != ')':
                terminating = i
                break
        prefix = prefix[:terminating]
        previousWord = prefix[::-1]

        #use MLE model
        if useMLE:
            #train on words
            tokens = nltk.word_tokenize(file)
            for i in range(len(tokens)):
                currentWord = tokens[i]
                if i != len(tokens)-1:
                    ngram = (currentWord, tokens[i+1])
                    ngramToCount[ngram] += 1
                wordCount[currentWord] += 1
                vocabSet.add(currentWord)
            #find each biagram prob
            wordList = []
            for word in vocabSet:
                if previousWord not in vocabSet:
                    break
                wordProb = (ngramToCount[(previousWord, word)] + 1) / (wordCount[previousWord] + len(vocabSet))
                wordList.append((wordProb, word))

            #return most likely word(s)
            wordList.sort(reverse=True)
            returnWords = []
            for pair in wordList[:3]:
                returnWords.append(pair[1])
            if len(returnWords) == 0:
                return ''
            return returnWords
        #Use Trie
        else:
            # tokenise the incoming file into individual characters, store these into a trie
            trie = CharTrie()
            for toknum, tokval, _, _, _ in tokenize(BytesIO(file.encode('utf-8')).readline):
                trie[tokval] = tokval
            try:
                return list(trie.values(previousWord))[:3]
            except KeyError:
                # no predictions
                return ''
            return file
