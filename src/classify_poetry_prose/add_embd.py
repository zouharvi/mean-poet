#!/usr/bin/env python3

import argparse
import tqdm
import pickle
from transformers import RobertaTokenizer, RobertaModel
import torch

DEVICE = "cuda:0" if torch.cuda.is_available() else "cpu"

def get_sentence_embd(text, tokenizer, model):
    with torch.no_grad():
        encoded_input = tokenizer(text, return_tensors='pt').to(DEVICE)
        # take the last hidden state and the first item in the batch
        output = model(**encoded_input)["last_hidden_state"][0]
        output_avg = torch.mean(output, dim=0).cpu().numpy()
    return output_avg

if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument(
        "-i", "--input", default="data_raw/dataset_class_prose.pkl",
        help="Path to input dataset file"
    )
    args.add_argument(
        "-o", "--output", default="data_raw/dataset_class_embd.pkl",
        help="Path to output dataset file"
    )
    args = args.parse_args()

    with open(args.input, "rb") as f:
        data = pickle.load(f)

    tokenizer = RobertaTokenizer.from_pretrained('roberta-large')
    model = RobertaModel.from_pretrained('roberta-large').to(DEVICE)
    model.eval()
    text = "Replace me by any text you'd like."
    data = [
        (get_sentence_embd(x, tokenizer, model), y)
        for x,y in tqdm.tqdm(data)
    ]

    with open(args.output, "wb") as f:
        pickle.dump(data, f)
