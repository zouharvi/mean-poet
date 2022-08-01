#!/usr/bin/env python3
import csv

from workers_evaluate import evaluate_translation
from constants import LABEL_REF
from collections import defaultdict
import numpy as np
import tqdm

COLUMN_MAP = {
    'Annotator': "annotator",
    'Title / author': "title_author",
    'Translator': "translator",
    'Original': "src",
    'Reference': "ref",
    'Translation': "tgt",
    'Meaning (1-5)': "meaning",
    'Poeticness (1-5)': "poeticness",
    'Overall (1-5)': "overall",
}
FEATURE_KEYS = [
    "meanpoet",

    "meter_sim_ref",
    "line_sim_ref",
    "rhyme_sim_ref",
    "meaning_overlap_ref",

    # standard metrics
    "bleu",
    "bertscore",
    "comet",

    # individual
    "rhyme_acc_ref",
    "rhyme_acc_tgt",
    "meter_reg_ref",
    "meter_reg_tgt",
]

with open("data/farewell_saarbrucken.csv", "r") as f:
    data = list(csv.DictReader(f))
    data = [{COLUMN_MAP[k]:v for k, v in item.items()} for item in data]

print("Read", len(data), "rows")

translator_scores = defaultdict(list)
for item_i, item in enumerate(tqdm.tqdm(data)):
    evaluation = evaluate_translation(
        radio_choice=LABEL_REF,
        poem_src=item["src"],
        poem_ref=item["ref"],
        poem_hyp=item["tgt"],
        return_dict=True,
    )
    for feature_key in FEATURE_KEYS:
        data[item_i][feature_key] = evaluation[feature_key]
    translator_scores[item["translator"]].append(item)

for translator, items in translator_scores.items():
    avg_meaning = np.average([float(x["meaning"]) for x in items])
    avg_poeticness = np.average([float(x["poeticness"]) for x in items])
    avg_overall = np.average([float(x["overall"]) for x in items])
    print(f"{translator+':':<20} {avg_meaning:>4.1f} {avg_poeticness:>4.1f} {avg_overall:>4.1f}")

with open("data/farewell_saarbrucken_f.csv", "w") as f:
    f = csv.DictWriter(f, fieldnames=data[0].keys())
    f.writeheader()
    f.writerows(data)

