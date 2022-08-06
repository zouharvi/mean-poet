#!/usr/bin/env python3
import csv

from metric.workers_evaluate import MeanPoet
from metric.constants import LABEL_REF
from collections import defaultdict
import numpy as np
import tqdm
import argparse

COLUMN_MAP = {
    'Annotator': "annotator",
    'Title / author': "title_author",
    'Translator': "translator",
    'Reference translator': "ref_translator",
    'Original': "src",
    'Reference': "ref",
    'Translation': "hyp",
    'Meaning (1-5)': "meaning",
    'Poeticness (1-5)': "poeticness",
    'Overall (1-5)': "overall",
}
FEATURE_KEYS = [
    "meanpoet",

    # abstractness
    "abstractness_ref",
    "abstractness_hyp",
    "abstractness_sim",
    
    "meter_sim_ref",
    "line_sim_ref",
    "rhyme_sim_ref",
    "meaning_overlap_ref",

    # standard metrics
    "bleu",

    # individual
    "rhyme_acc_ref",
    "rhyme_acc_hyp",
    "meter_reg_ref",
    "meter_reg_hyp",
]

FEATURE_KEYS_HEAVY = [
    "bertscore",
    "comet",
]

if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument(
        "-i", "--input",
        default=["data/farewell_saarbrucken.csv"], nargs="+"
    )
    args.add_argument("-o", "--output", default="data/tmp_f.csv")
    args.add_argument("-H", "--heavy", action="store_true")
    args = args.parse_args()

    if args.heavy:
        FEATURE_KEYS += FEATURE_KEYS_HEAVY

    data = []
    for f in args.input:
        with open(f, "r") as f:
            data += [
                {COLUMN_MAP[k]:v for k, v in item.items()}
                for item in csv.DictReader(f)
            ]

    print("Read", len(data), "rows")

    metric = MeanPoet(heavy=False)

    translator_scores = defaultdict(list)
    for item_i, item in enumerate(tqdm.tqdm(data)):
        evaluation = metric.evaluate_translation(
            radio_choice=LABEL_REF,
            poem_src=item["src"],
            poem_ref=item["ref"],
            poem_hyp=item["hyp"],
            return_dict=True,
        )
        for feature_key in FEATURE_KEYS:
            data[item_i][feature_key] = evaluation[feature_key]
        translator_scores[item["translator"]].append(item)

    for translator, items in translator_scores.items():
        avg_meaning = np.average([float(x["meaning"]) for x in items])
        avg_poeticness = np.average([float(x["poeticness"]) for x in items])
        avg_overall = np.average([float(x["overall"]) for x in items])
        print(
            f"{translator+':':<20} {avg_meaning:>4.1f} {avg_poeticness:>4.1f} {avg_overall:>4.1f}")

    print("Saving to", args.output)

    with open(args.output, "w") as f:
        f = csv.DictWriter(f, fieldnames=data[0].keys())
        f.writeheader()
        f.writerows(data)
