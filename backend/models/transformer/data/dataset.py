from data.vocab import CharVocab
import random
import torch
import pickle
import os
from torch.utils.data import Dataset
import numpy as np

class Character_Level_Dataset(Dataset):
    def __init__(self, train_data_path, block_size):
        print(f"Block Size: {block_size}")
        self.block_size = block_size
        with open(os.path.join(train_data_path, 'file_array.pkl'), 'rb') as file:
            self.data = pickle.load(file)

        self.vocab = CharVocab()
        print(f'Data consists of {len(self.vocab.stoi)} unique characters')

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        file = self.data[idx]
        # get a random segment from the file, of length less than block size - 1

        # get a segment length between 10 and the minimum of the length of the file, and the block size - 1
        segment_length = np.random.randint(10, min(len(file), self.block_size - 2))
        starting_point = np.random.randint(0, len(self.data[idx]) - segment_length)

        file_segment = file[starting_point:starting_point + segment_length]
        file_segment = file_segment + self.vocab.PAD_CHAR * (self.block_size - len(file_segment))

        x = file_segment[:-1]
        y = file_segment[1:]

        # print("Here are the examples:")
        # print()
        # print()
        # print('x:\n\n\n')
        # print(x)
        # print('y: \n\n\n')
        # print(y)

        x = torch.tensor([self.vocab.stoi[c] for c in x], dtype=torch.long)
        y = torch.tensor([self.vocab.stoi[c] for c in y], dtype=torch.long)

        return x, y
