#!/usr/bin/env python3
import csv

from metric.workers_evaluate import MeanPoet
from metric.constants import LABEL_REF
from collections import defaultdict
import tqdm
import argparse

from utils import json_dumpl, json_readl

FEATURE_KEYS = [
    "meanpoet",

    # others
    "pos_dist_sim",

    # abstractness
    "abstractness_ref",
    "abstractness_hyp",
    "abstractness_sim",

    # general similarities
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
        default=[
            "data_annotations/parsed_flat_train.jsonl",
            "data_annotations/parsed_flat_dev.jsonl"
        ]
    )
    args.add_argument("-H", "--heavy", action="store_true")
    args = args.parse_args()

    if args.heavy:
        FEATURE_KEYS += FEATURE_KEYS_HEAVY

    print("Loading metric")
    metric = MeanPoet(heavy=args.heavy)

    for fname in args.input:
        data = json_readl(fname)
        print("Read", len(data), "rows from", fname)

        translator_scores = defaultdict(list)
        for item_i, item in enumerate(tqdm.tqdm(data)):
            evaluation = metric.evaluate_translation(
                radio_choice=LABEL_REF,
                poem_src=item["src"] if "src" in item else "",
                poem_ref=item["ref"],
                poem_hyp=item["hyp"],
                return_dict=True,
            )
            for feature_key in FEATURE_KEYS:
                data[item_i][feature_key] = evaluation[feature_key]
            translator_scores[item["translator"]].append(item)

        fnameout = fname.replace(".jsonl", "_f.jsonl")
        print("Saving to", fnameout)
        json_dumpl(fnameout, data)
