import torch
from models.base import BaseModel
from models.transformer.model.model import GPT
from models.transformer.model.model import GPTConfig
from models.transformer.data.vocab import BaseVocab
import models.transformer.utils.utils as utils
import sys
sys.path.insert(0, './models/transformer') 
# ^^ don't ask... Pickle sucks sometimes, and Pytorch relies on Pickle.  
# Without this line torch.load() can't be run from a directory other 
# than the directory where the model was originally created; i.e. 
# in ./models/transformer

class TransformerModel(BaseModel):

    # load the model parameters from the checkpoint path, and initialise the model
    # ready to run inference (should be reasonably small; around 60mb per model).
    # Therefore, we should be able to scale this relatively easily to one model per
    # user in a session...  Which opens the door for per-user pretraining.
    def __init__(self, param_path):
        super().__init__(name='transformer_model')
        self.device = 'cpu'
        self.num_predictions = 3
        self.ckpt = torch.load(param_path, map_location=torch.device(self.device))
        model_config = self.ckpt['model_config']
        self.itos = self.ckpt['itos']
        self.stoi = self.ckpt['stoi']

        # build model config
        mconf = GPTConfig(
            vocab_size=len(self.itos),
            args_dict=model_config.__dict__
        )

        # load model weights
        self.gpt_model = GPT(mconf)
        self.gpt_model = self.gpt_model.to(self.device)

        self.gpt_model.load_state_dict(self.ckpt['state_dict'])
        self.block_size = model_config.__dict__['block_size']
        print(f"Block size: {self.block_size}")

    def predict(self, file, cursor_index):
        # grab the preceeding self.block_size (if possible) characters from file
        prediction_length = 20
        preceding_file = file[max(0, cursor_index - self.block_size + prediction_length + 2):cursor_index]

        x = []
        for char in preceding_file:
            try:
                vocab_idx = self.stoi[char]
            except KeyError:
                print("WARNING: We've got an UNK!")
                print("code_str = ", preceding_file)
                print("Move = ", char)
                vocab_idx = self.stoi[BaseVocab().UNK]
            x.append(vocab_idx)

        x = torch.tensor(x, dtype=torch.long)[None,...].to(self.device)

        prefix = file[:cursor_index:][::-1]
        terminating = len(prefix) - 1
        for i in range(len(prefix)):
            if not prefix[i].isalpha() and prefix[i] != '_':
                terminating = i
                break

        prefix = prefix[:terminating]
        prefix = prefix[::-1]

        predictions = []
        for i in range(self.num_predictions):
            pred = utils.sample(self.gpt_model, x, 20, sample=(False if i == 0 else True))[0]
            full_prediction = ''.join([self.itos[int(i)] for i in pred][len(preceding_file):])
            
            # if we predict the EOL; we just want to cut the prediction there
            EOL_index = full_prediction.find('\n')
            if EOL_index != -1:
                full_prediction = full_prediction[:EOL_index]

            predictions.append(prefix + full_prediction)
            
            # there's probably some other logic that we'll find on how we want to constrain
            # what can be predicted here; we can add that later as and when it occurs

        return [predictions]

    def finetune(self, files):
        raise NotImplemented