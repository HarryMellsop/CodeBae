from data.vocab import BaseVocab
from model import model
from utils import utils
import questionary
import os
import torch
import argparse

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# device = torch.cuda.current_device() if torch.cuda.is_available() else 'cpu'
device = 'cpu'

def get_prediction(code_str, gpt_model, stoi, itos, sample=False):
    """
    Extract a prediction from a given model, given a string of code
    """
    
    x = []
    for char in code_str:
        try:
            vocab_idx = stoi[char]
        except KeyError:
            print("WARNING: We've got an UNK!")
            print("code_str = ", code_str)
            print("Move = ", char)
            vocab_idx = stoi[BaseVocab().UNK]
        x.append(vocab_idx)

    x = torch.tensor(x, dtype=torch.long)[None,...].to(device)

    pred = utils.sample(gpt_model, x, 20, sample=sample)[0]
    return ''.join([itos[int(i)] for i in pred][len(code_str):])
    # TODO: MORE TO COME HERE; JUST WANT TO TEST TO SEE WHAT WE'RE GETTING OUT THE OTHER SIDE

# Get the most recent parameters file from the ckpts
def get_recent_ckpt(ckpt_dir):

    if not os.path.isdir(ckpt_dir):
        raise ValueError(f"Default checkpoint dir at {ckpt_dir} missing!")

    files = os.listdir(ckpt_dir)
    if 'best_loss.pt' in files:
        answer = questionary.confirm("File best_loss.pt found. Use this file?").ask()
        if answer:
            return os.path.join(ckpt_dir, 'best_loss.pt')
    epoch_list = [x for x in files if 'epoch' in x]
    if len(epoch_list) > 0:
        answer = questionary.confirm("Epoch files found. Use best epoch file?").ask()
        if answer:
            epoch_list.sort(key=lambda x: int(x.split('_')[1].split('.')[0]), reverse=True)
            return os.path.join(ckpt_dir, epoch_list[0])

    iter_list = [x for x in files if 'iter' in x]
    iter_list.sort(key=lambda x: int(x.split('_')[1].split('.')[0]), reverse=True)

    return os.path.join(ckpt_dir, iter_list[0])

if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('--with-params', type=str, help='Parameters to use for evaluation script')

    args = parser.parse_args()

    # load the GPT model from the parameters
    if args.with_params:
        print(f'Loading provided parameters from {args.with_params}')
        ckpt_path = args.with_params
    else:
        ckpt_path = get_recent_ckpt('./ckpts/training_checkpoints')
        print(f'Loading most recent parameters: {ckpt_path}')
    ckpt = torch.load(ckpt_path, map_location=torch.device(device))
    model_config = ckpt['model_config']
    itos = ckpt['itos']
    stoi = ckpt['stoi']

    # build model config
    mconf = model.GPTConfig(
        vocab_size=len(itos),
        args_dict=model_config.__dict__
    )

    # load model weights
    gpt_model = model.GPT(mconf)
    gpt_model = gpt_model.to(device)

    gpt_model.load_state_dict(ckpt['state_dict'])

    # temporary naive prediction logic

    while True:
        code_str = input(f"Enter some code to autocomplete: ")
        pred = get_prediction(code_str, gpt_model, stoi, itos)
        print(f"My prediction is: {bcolors.WARNING}{code_str}{bcolors.OKCYAN}{pred}{bcolors.ENDC}")
        