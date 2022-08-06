#!/usr/bin/env python3
import csv

from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import numpy as np
import argparse

# TARGET= "meaning"
# TARGET= "poeticness"
TARGET = "overall"
FEATURE_KEYS = [
    # metrics
    "bleu",
    # "bertscore",
    # "comet",

    # similarity
    "abstractness_hyp",
    "abstractness_ref",
    "meter_sim_ref",
    "line_sim_ref",
    "rhyme_sim_ref",
    "meaning_overlap_ref",

    # individual
    # "rhyme_acc_ref",
    "rhyme_acc_hyp",
    # "meter_reg_ref",
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
    xs = [x[feature_index] for x, y in data]
    corr = np.corrcoef(ys, xs)[0, 1]
    print(f"Corr {corr:>5.2f} ({feature})")


if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument(
        "-i", "--input", default=["data/farewell_saarbrucken_f.csv"], nargs="+")
    args.add_argument("-H", "--heavy", action="store_true")
    args = args.parse_args()

    data = []
    for f in args.input:
        with open(f, "r") as f:
            data += [
                ([float(item[f]) for f in FEATURE_KEYS], float(item[TARGET]))
                for item in csv.DictReader(f)
            ]
    ys = [y for x, y in data]
    xs = [x for x, y in data]

    xs = StandardScaler().fit_transform(np.array(xs))

    model = LinearRegression()

    model.fit(
        xs,
        ys,
    )
    y_pred = model.predict([x for x, y in data])
    explain_model(model)
    mae = np.average([
        abs(y - y_pred)
        for y, y_pred
        in zip(ys, y_pred)
    ])
    corr = np.corrcoef(ys, y_pred)[0, 1]
    print(f"MAE  {mae:>5.2f} (LR)")
    print(f"Corr {corr:>5.2f} (LR)")

    correlate_feature("bleu", ys, xs)
    correlate_feature("bertscore", ys, xs)
    correlate_feature("comet", ys, xs)
