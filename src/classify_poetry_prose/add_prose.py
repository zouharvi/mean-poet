#!/usr/bin/env python3

import argparse
import pickle
import datasets
if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument(
        "-i", "--input", default="data_raw/dataset_class_parap.pkl",
        help="Path to input dataset file"
    )
    args.add_argument(
        "-o", "--output", default="data_raw/dataset_class_prose.pkl",
        help="Path to output dataset file"
    )
    args = args.parse_args()

    with open(args.input, "rb") as f:
        data = pickle.load(f)

    prose = iter(datasets.load_dataset("opus_books", "de-en")["train"])

    # we have 4 classes, so balance it out
    target_len = len(data)//4
    new_data = []
    while len(new_data) < target_len:
        sent = next(prose)["translation"]["en"]
        if len(sent.split()) >= 10:
            new_data.append((sent, "prose"))
            print((sent,"prose"))

    print("saving", len(data)+len(new_data), "in total")
    print("new sentences:", len(new_data))
    with open(args.output, "wb") as f:
        pickle.dump(data+new_data, f)
