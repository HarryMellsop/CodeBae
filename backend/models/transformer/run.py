import argparse
from data import dataset
from model import model
from model import trainer
from utils import utils
import questionary
import torch
import os


def main(config_args, train_args, save_dir, data_dir, pretrain_state=None):

    # Get ckpt state if we are re-loading from ckpt
    if pretrain_state:
        state_dict = pretrain_state['state_dict']
    else:
        state_dict = None

    # get device
    device = torch.cuda.current_device() if torch.cuda.is_available() else 'cpu'
    print("DEVICE: {}".format(device))

    # build datasets
    print('\nProcessing dataset...')

    train_dataset = dataset.Character_Level_Dataset(data_dir, config_args["block_size"])
    # load model
    mconf = model.GPTConfig(
        vocab_size=train_dataset.vocab.vocab_size,
        args_dict=config_args
    )

    # build model
    gpt_model = model.GPT(mconf)
    gpt_model = gpt_model.to(device)

    train_config = trainer.TrainerConfig(state_dict=state_dict,
                                         args_dict=train_args)

    model_trainer = trainer.Trainer(gpt_model,
                                    train_dataset,
                                    save_dir,
                                    config=train_config)
    model_trainer.train()


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument('--resume-from', type=str, help='Path to model parameters to resume training from')
    args = parser.parse_args()

    data_dir = 'data/datasets-cleaned'
    save_dir = os.path.join('ckpts', 'training_checkpoints')

    if not os.path.isdir(save_dir):
        os.makedirs(save_dir) 

    config_args = utils.default_config_args
    train_args = utils.default_train_args

    device = torch.cuda.current_device() if torch.cuda.is_available() else 'cpu'

    ckpt_dict = None
    if args.resume_from:
        print(f"Resuming from {args.resume_from}")
        ckpt_dict = torch.load(args.resume_from, map_location=torch.device(device))

    main(config_args, train_args, save_dir, data_dir, pretrain_state=ckpt_dict)
