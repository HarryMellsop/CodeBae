import torch
from models.base import BaseModel

class TransformerModel(BaseModel):

    def __init__(self):
        super().__init__(name='transformer_model')

    # this parameters parameter should be an opened pytorch param file trained using the default
    # model parameters as saved.
    def predict(self, parameters, cursor_index):
        pass