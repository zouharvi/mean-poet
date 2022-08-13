#!/usr/bin/env python3

import argparse
import pickle
import datasets
if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument(
        "-i", "--input", default="computed/dataset_class_parap.pkl",
        help="Path to input dataset file"
    )
    args.add_argument(
        "-o", "--output", default="computed/dataset_class_prose.pkl",
        help="Path to output dataset file"
    )
    args = args.parse_args()

    with open(args.input, "rb") as f:
        data = pickle.load(f)

    books = iter(datasets.load_dataset("opus_books", "de-en")["train"])
    news = iter(datasets.load_dataset("wmt19", "cs-en")["train"])

    # we have 4 classes, so balance it out
    target_len = len(data)//4
    new_data_books = []
    while len(new_data_books) < target_len:
        sent = next(books)["translation"]["en"]
        if len(sent.split()) >= 10:
            new_data_books.append((sent, "books"))
            print((sent,"books"))

    new_data_news = []
    while len(new_data_news) < target_len:
        sent = next(news)["translation"]["en"]
        if len(sent.split()) >= 10:
            new_data_news.append((sent, "news"))
            print((sent,"news"))

    print("saving", len(data)+len(new_data_books)+len(new_data_news), "in total")
    print("new sentences books:", len(new_data_books))
    print("new sentences news: ", len(new_data_news))
    with open(args.output, "wb") as f:
        pickle.dump(data+new_data_books+new_data_news, f)
