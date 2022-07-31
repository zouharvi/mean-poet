#!/usr/bin/env python3
import csv

from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import numpy as np


# TARGET= "meaning"
# TARGET= "poeticness"
TARGET = "overall"
FEATURE_KEYS = [
    "meter_sim_ref",
    "line_sim_ref",
    "rhyme_sim_ref",
    "bleu_ref",
    "meaning_overlap_ref",

    # individual
    "rhyme_acc_ref",
    "rhyme_acc_tgt",
    "meter_reg_ref",
    "meter_reg_tgt",
]

def explain_model(model):
    print()
    print(f"Bias: {model.intercept_:.2f}")
    for feature_i, feature in enumerate(FEATURE_KEYS):
        print(f"{feature+':':<25} {model.coef_[feature_i]:>5.2f}")
    print()
        

if __name__ == "__main__":
    with open("data/farewell_saarbrucken_f.csv", "r") as f:
        data = [([float(item[f]) for f in FEATURE_KEYS], float(item[TARGET]))
                for item in csv.DictReader(f)]
    ys = [y for x, y in data]
    xs = [x for x, y in data]

    xs = StandardScaler().fit_transform(np.array(xs))

    model = LinearRegression()

    # TODO: standardize
    model.fit(
        xs,
        ys,
    )
    y_pred = model.predict([x for x, y in data])
    mae = np.average([
        abs(y - y_pred)
        for y, y_pred
        in zip(ys, y_pred)
    ])
    print(f"MAE {mae:.2f} (LR)")
    explain_model(model)

    y_pred = [np.average(ys)]*len(data)
    mae = np.average([
        abs(y - y_pred)
        for y, y_pred
        in zip(ys, y_pred)
    ])
    print(f"MAE {mae:.2f} (dummy)")

    bleu_index = FEATURE_KEYS.index("bleu_ref")
    model.fit(
        [[x[bleu_index]] for x, y in data],
        ys,
    )
    y_pred = model.predict(
        [[x[bleu_index]] for x, y in data]
    )
    mae = np.average([
        abs(y - y_pred)
        for y, y_pred
        in zip(ys, y_pred)
    ])
    print(f"MAE {mae:.2f} (BLEU)")