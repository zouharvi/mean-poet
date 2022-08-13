#!/usr/bin/env python3

import argparse
import pickle
import numpy as np
from utils_local import *

def sim(x, y):
    return np.inner(x,y)/(np.linalg.norm(x)*np.linalg.norm(y))

# we're computing contrastive pairs for which we don't have examples here
# TODO: we could still measure how much roundtrip translation changes it
# the hypothesis is that less than poetry
CATEGORIES.remove("books")
CATEGORIES.remove("news")

if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument(
        "-d", "--dataset", default="computed/dataset_class_embd.pkl",
        help="Path to embedding file"
    )
    args = args.parse_args()

    with open(args.dataset, "rb") as f:
        data = pickle.load(f)

    # this assumes that the data has not been shuffled and preserve the structure of `generate_paraphrases.py`
    data = {
        "orig": [x for x, y in data if y == "orig"],
        "orig_parap": [x for x, y in data if y == "orig_parap"],
        "line": [x for x, y in data if y == "line"],
        "line_parap": [x for x, y in data if y == "line_parap"],
        "books": [x for x, y in data if y == "books"],
        "news": [x for x, y in data if y == "news"],
    }

    results_contrast = {}
    results_all_all = {}

    # we're doing twice as much work but it doesn't matter
    for cat1 in CATEGORIES:
        for cat2 in CATEGORIES:
            results_contrast[(cat1,cat2)] = np.average([sim(x,y) for x,y in zip(data[cat1], data[cat2])])
            results_all_all[(cat1,cat2)] = np.average([sim(x,y) for x in data[cat1] for y in data[cat2]])
    
    for cat1 in CATEGORIES:
        results_all_all[(cat1,"books")] = np.average([sim(x,y) for x in data[cat1] for y in data["books"]])
        results_all_all[(cat1,"news")] = np.average([sim(x,y) for x in data[cat1] for y in data["news"]])
    
    results_all_all[("news","books")] = np.average([sim(x,y) for x in data["books"] for y in data["news"]])
    results_all_all[("books","news")] = np.average([sim(x,y) for x in data["books"] for y in data["news"]])

    print(results_contrast)
    print()
    print(results_all_all)