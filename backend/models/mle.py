from collections import defaultdict
from models.base import BaseModel

from nltk.tokenize import word_tokenize
import nltk
nltk.download('punkt')

class MLEModel(BaseModel):
    finetune_implemented = False

    def __init__(self):
        super().__init__(name='mle_model')

    def predict(self, file, cursor_index):
        ngramToCount = defaultdict(float)
        wordCount = defaultdict(float)
        vocabSet = set()

        # train on words
        tokens = nltk.word_tokenize(file)
        for i in range(len(tokens)):
            currentWord = tokens[i]
            if i != len(tokens)-1:
                ngram = (currentWord, tokens[i+1])
                ngramToCount[ngram] += 1
            wordCount[currentWord] += 1
            vocabSet.add(currentWord)

        # get previous word
        prefix = file[0:cursor_index:]
        prefix = prefix[::-1]
        terminating = len(prefix) - 1
        for i in range(len(prefix)):
            if not prefix[i].isalpha() and prefix[i] != '_':
                terminating = i
                break
        prefix = prefix[:terminating]
        previousWord = prefix[::-1]

        # find each biagram prob
        wordList = []
        for word in vocabSet:
            if previousWord not in vocabSet:
                break
            wordProb = (ngramToCount[(previousWord, word)] + 1) / (wordCount[previousWord] + len(vocabSet))
            wordList.append((wordProb, word))

        # return most likely word(s)
        wordList.sort(reverse=True)
        returnWords = []
        for pair in wordList[:3]:
            returnWords.append(' ' + pair[1])

        if len(returnWords) == 0:
            return ''

        return returnWords