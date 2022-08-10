#!/usr/bin/env python3

import argparse
import pickle
import numpy as np


def sim(x, y):
    return np.inner(x,y)/(np.linalg.norm(x)*np.linalg.norm(y))

# WARNING: this does not have prose
CATEGORIES = ["orig", "line", "orig_parap", "line_parap"]

if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument(
        "-d", "--dataset", default="data_raw/dataset_class_embd.pkl",
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
        "prose": [x for x, y in data if y == "prose"],
    }

    results_contrast = {}
    results_all_all = {}

    # we're doing twice as much work but it doesn't matter
    for cat1 in CATEGORIES:
        for cat2 in CATEGORIES:
            results_contrast[(cat1,cat2)] = np.average([sim(x,y) for x,y in zip(data[cat1], data[cat2])])
            results_all_all[(cat1,cat2)] = np.average([sim(x,y) for x in data[cat1] for y in data[cat2]])
    
    for cat1 in CATEGORIES:
        results_all_all[(cat1,"prose")] = np.average([sim(x,y) for x in data[cat1] for y in data["prose"]])

    print(results_contrast)
    print()
    print(results_all_all)