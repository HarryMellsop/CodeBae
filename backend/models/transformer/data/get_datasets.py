import os
import argparse
import glob
import pickle
import tqdm
import string
import time

def download_datasets():

    print("Downloading the Python Code Corpus Dataset")
    if os.path.exists('./data/datasets/python-corpus.tar.gz'):
        print("Raw python corpus found.")
    else:
        print("Now downloading raw python corpus...")
        os.system('curl -O https://ndownloader.figshare.com/articles/11777217/versions/1')
        os.system('mv 1 data/datasets/1')

    if os.path.exists('./data/datasets/python-corpus/cleaned'):
        print('Python Corpus already extracted')
    else:
        print('Attempting to extract the dataset...')
        os.system('unzip ./data/datasets/1 -d ./data/datasets')
        os.system('tar -zxf ./data/datasets/python-corpus.tar.gz -C ./data/datasets --checkpoint=10000')

def preprocess_corpus():
    legal_characters = string.punctuation + string.ascii_lowercase + string.ascii_uppercase + '0123456789' + ' ' + '\n' + '\t'
    file_array = []
    iter = 0
    # run through every file in the python corpus, load that file into one mega list where each file is a string within the list
    for filename in tqdm.tqdm(glob.iglob('./data/datasets/python-corpus/cleaned/' + '**/**', recursive=True)):
        if iter >= 1e6: break # limit us to 1 million training examples, for now
        try:
            with open(filename, 'r') as file:
                try:
                    code = file.read()
                    # check that the code only contains punctuation/numbers/ascii and is of reasonable length to be relevant
                    if len(code) <= 50: continue
                    add = True
                    for char in code:
                        if char not in legal_characters:
                            add = False
                            break
                    if add:
                        iter += 1
                        file_array.append(code)
                        if iter % 50000 == 0: print(f'Added {iter} documents to the list')
                except:
                    pass
        except IsADirectoryError:
            pass

    with open('./data/datasets-cleaned/file_array.pkl', 'wb') as f:
        pickle.dump(file_array, f, pickle.HIGHEST_PROTOCOL)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument('--download', action='store_true')
    parser.add_argument('--preprocess', action='store_true')

    args = parser.parse_args()
    
    if args.download:
        download_datasets()
        
    if args.preprocess:
        try:
            preprocess_corpus()
        except FileNotFoundError:
            print('Python corpus not found!')