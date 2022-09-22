#!/usr/bin/env python3
from collections import defaultdict
import copy
import tqdm

from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import numpy as np
import argparse

from utils import json_readl

# TARGET= "meaning"
# TARGET= "poeticness"
TARGET = "overall"
FEATURE_KEYS = [
    # metrics
    "bleu",
    "bertscore",
    "comet",

    # others
    "pos_dist_sim",

    # abstractness
    # "abstractness_ref",
    # "abstractness_hyp",
    # "abstractness_sim",

    # general similarities
    "meter_sim_ref",
    "line_sim_ref",
    "rhyme_sim_ref",
    "meaning_overlap_ref",

    # individual
    "rhyme_acc_ref",
    "rhyme_acc_hyp",
    "meter_reg_ref",
    "meter_reg_hyp",
]


def explain_model(model):
    print()
    print(f"Bias: {model.intercept_:.2f}")
    for feature_i, feature in enumerate(FEATURE_KEYS):
        print(f"{feature+':':<25} {model.coef_[feature_i]:>5.2f}")
    print()


def correlate_feature(feature, ys, xs):
    feature_index = FEATURE_KEYS.index(feature)
    xs = [x[feature_index] for x in xs]
    corr = np.corrcoef(ys, xs)[0, 1]
    return corr


if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument(
        "-dt", "--data-train", default="data_annotations/parsed_flat_train_f.jsonl"
    )
    args.add_argument(
        "-dd", "--data-dev", default="data_annotations/parsed_flat_dev_f.jsonl"
    )
    args.add_argument(
        "-sc", "--seed-count", type=int, default=100
    )
    args = args.parse_args()

    data_train = json_readl(args.data_train)
    data_dev = json_readl(args.data_dev)
    output_logs = defaultdict(list)
    data_readonly = data_train + data_dev

    for seed in tqdm.tqdm(range(args.seed_count), total=args.seed_count):
        # redistribute train/dev split
        data = copy.deepcopy(data_readonly)
        data_poems = defaultdict(list)
        for line in data:
            data_poems[line["hyp"]].append(line)
        data_train, data_dev = train_test_split(
            list(data_poems.values()), test_size=31, random_state=seed)
        data_train = [l for ls in data_train for l in ls]
        data_dev = [l for ls in data_dev for l in ls]

        data_train = [
            ([float(item[f]) for f in FEATURE_KEYS], float(item[TARGET]))
            for item
            in data_train
            if item[TARGET] is not None
        ]
        data_dev = [
            ([float(item[f]) for f in FEATURE_KEYS], float(item[TARGET]))
            for item
            in data_dev
            if item[TARGET] is not None
        ]

        ys_train = [y for x, y in data_train]
        xs_train = [x for x, y in data_train]
        ys_dev = [y for x, y in data_dev]
        xs_dev = [x for x, y in data_dev]

        scaler = StandardScaler()
        scaler.fit(xs_train + xs_dev)
        xs_train = scaler.transform(np.array(xs_train))
        xs_dev = scaler.transform(np.array(xs_dev))

        model = LinearRegression()

        model.fit(
            xs_train, ys_train,
        )
        ys_pred_train = model.predict(xs_train)
        ys_pred_dev = model.predict(xs_dev)
        # explain_model(model)

        def get_mae(ys, ys_pred):
            return np.average([
                abs(y - y_pred)
                for y, y_pred
                in zip(ys, ys_pred)
            ])

        mae_train = get_mae(ys_train, ys_pred_train)
        mae_dev = get_mae(ys_dev, ys_pred_dev)
        output_logs["MAE train (LR)"] = mae_train
        output_logs["MAE dev (LR)"] = mae_dev

        corr_train = np.corrcoef(ys_train, ys_pred_train)[0, 1]
        corr_dev = np.corrcoef(ys_dev, ys_pred_dev)[0, 1]
        output_logs["Corr train (LR)"] = corr_train
        output_logs["Corr dev (LR)"] = corr_dev

        for metric in ["bleu", "bertscore", "comet"]:
            if metric not in FEATURE_KEYS:
                continue
            corr = correlate_feature(metric, ys_train, xs_train)
            output_logs[f"Corr train ({metric})"] = corr
            corr = correlate_feature(metric, ys_dev, xs_dev)
            output_logs[f"Corr dev ({metric})"] = corr

    for name, values in output_logs.items():
        print(f"{name:>25}: {np.average(values):.3f}")