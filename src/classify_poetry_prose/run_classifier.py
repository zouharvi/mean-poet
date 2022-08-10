#!/usr/bin/env python3

import argparse
from audioop import avg
import tqdm
import pickle
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import KFold
import numpy as np


def evaluate_two_categories_cv(data, cat1, cat2, cv=10):
    data = [(x, y) for x, y in data if y == cat1 or y == cat2]
    data_x = np.array([x for x, y in data])
    data_y = np.array([y for x, y in data])

    if cv is None:
        cv = len(data)

    acc_c12 = []

    for train_i, test_i in tqdm.tqdm(list(KFold(n_splits=cv).split(data_x, data_y))):
        train_x = data_x[train_i]
        train_y = data_y[train_i]
        test_x = data_x[test_i]
        test_y = data_y[test_i]

        model = LogisticRegression(max_iter=300, C=0.5)
        model.fit(train_x, train_y)
        acc = model.score(test_x, test_y)
        acc_c12.append(acc)
    avg_acc = np.average(acc_c12)
    print(f"{cat1}-{cat2}: {avg_acc:.2%}")

    return {(cat1, cat2): avg_acc}

CATEGORIES = ["orig", "line", "orig_parap", "line_parap", "prose"]

if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument(
        "-i", "--input", default="data_raw/dataset_class_embd.pkl",
        help="Path to input dataset file"
    )
    args = args.parse_args()

    with open(args.input, "rb") as f:
        data = pickle.load(f)

    data_x = [x for x, y in data]
    data_y = [y for x, y in data]
    # label_encoder = LabelEncoder()
    # data_y = label_encoder.fit_transform(data_y)
    data_x = StandardScaler().fit_transform(data_x)
    data = list(zip(data_x, data_y))

    results = {}
    for i in range(len(CATEGORIES) - 1):
        for j in range(i + 1, len(CATEGORIES)):
            results |= evaluate_two_categories_cv(
                data,
                cat1=CATEGORIES[i],
                cat2=CATEGORIES[j],
                cv=None
            )

    print(results)