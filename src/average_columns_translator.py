#!/usr/bin/env python3
import csv
from collections import defaultdict
import numpy as np

FEATURE_KEYS = [
    # standard metrics
    "bleu",
    "bertscore",
    "comet",

    # human evaluation
    "meaning",
    "poeticness",
    "overall",

    # detected
    "meanpoet",
    "meter_sim_ref",
    "line_sim_ref",
    "rhyme_sim_ref",

    # individual
    "meaning_overlap_ref",
    "rhyme_acc_tgt",
    "meter_reg_tgt",
]

if __name__ == "__main__":
    with open("data/farewell_saarbrucken_f.csv", "r") as f:
        data = [
            {
                f:float(item[f]) for f in FEATURE_KEYS} | {"translator": item["translator"]}
            for item in csv.DictReader(f)
        ]


    data_translators = defaultdict(list)
    for item in data:
        data_translators[item["translator"]].append(item)


    for translator, translator_v in data_translators.items():
        print("{:<20}".format(translator+ ':'), end="")
        for feature in FEATURE_KEYS:
            print("{:<5.2f}".format(np.average([x[feature] for x in translator_v])), end="")
        print()