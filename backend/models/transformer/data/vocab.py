from tqdm import tqdm
import numpy as np
import string
import pickle
import os
import questionary

class BaseVocab:
    def __init__(self):
        self.PAD_CHAR = u"\u25A1"
        self.MASK_CHAR_1 = u"\u2047"
        self.MASK_CHAR_2 = u"\u2048"
        self.UNK = u"\u2049"

class CharVocab(BaseVocab):
    def __init__(self):
        super().__init__()

        chars = [char for char in (string.punctuation + string.ascii_lowercase + string.ascii_uppercase + '0123456789' + ' ' + '\n' + '\t')]

        # Insert sentinel characters
        chars.append(self.PAD_CHAR)
        chars.append(self.MASK_CHAR_1)
        chars.append(self.MASK_CHAR_2)

        # ensure that we have no duplicates
        chars = list(set(chars))

        self.stoi = {i:n for n, i in enumerate(chars)}
        self.itos = {n:i for n, i in enumerate(chars)}
        self.vocab_size = len(self.stoi)

        assert len(self.stoi) == len(self.itos)