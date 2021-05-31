from collections import defaultdict
from pygtrie import CharTrie
from io import BytesIO
from tokenize import tokenize
from models.base import BaseModel

from nltk.tokenize import word_tokenize
import nltk
nltk.download('punkt')

class ComboModel(BaseModel):
    finetune_implemented = True

    def __init__(self):
        super().__init__(name='combo_model')

    def predict(self, file, cursor_index, use_finetune=True):
        ngramToCount = defaultdict(float)
        wordCount = defaultdict(float)
        vocabSet = set()
        useMLE = False

        # get previous word
        prefix = file[0:cursor_index:]
        prefix = prefix[::-1]
        terminating = len(prefix)

        # decide whether to use mle or trie
        # if not either of these cases, use trie as default
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

        # use MLE model
        if useMLE:
            if use_finetune and self.finetuned:
                ngramToCount = self.ft_ngramToCount
                vocabSet = self.ft_vocabSet
                wordCount = self.ft_wordCount
            
            # train on words
            tokens = nltk.word_tokenize(file)
            for i in range(len(tokens)):
                currentWord = tokens[i]
                if i != len(tokens)-1:
                    ngram = (currentWord, tokens[i+1])
                    ngramToCount[ngram] += 1
                wordCount[currentWord] += 1
                vocabSet.add(currentWord)
            
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
                returnWords.append(pair[1])
            if len(returnWords) == 0:
                return ''
            return returnWords

        # use trie
        else:
            if use_finetune and self.finetuned:
                trie = self.ft_trie
            else:
                trie = CharTrie()
            
            # tokenise the incoming file into individual characters, store these into a trie
            for toknum, tokval, _, _, _ in tokenize(BytesIO(file.encode('utf-8')).readline):
                if tokval == 'utf-8' or toknum == 0: continue
                trie[tokval] = tokval
            
            if previousWord in trie.keys():
                del trie[previousWord]
            
            try:
                return list(trie.values(previousWord))[:3]
            except KeyError:
                
                # no predictions
                return ''

            return file

    def finetune(self, files):
        trie = CharTrie()
        
        # finetune trie on multiple files
        for toknum, tokval, _, _, _ in tokenize(BytesIO(files.encode('utf-8')).readline):
            if tokval == 'utf-8' or toknum == 0: continue
            trie[tokval] = tokval
        
        # set finetuned internally
        self.ft_trie = trie

        tokens = nltk.word_tokenize(files)
        for i in range(len(tokens)):
            currentWord = tokens[i]
            if i != len(tokens)-1:
                ngram = (currentWord, tokens[i+1])
                ngramToCount[ngram] += 1

            wordCount[currentWord] += 1
            vocabSet.add(currentWord)

        self.finetuned = True
        self.ft_ngramToCount = ngramToCount
        self.ft_wordCount = wordCount
        self.ft_vocabSet = vocabSet
