#!/usr/bin/env python3
import csv

from workers_evaluate import evaluate_translation
from constants import LABEL_REF

COLUMN_MAP = {
    'Title / author': "bio",
    'Original': "src",
    'Reference': "ref",
    'Translation': "tgt",
    'Meaning (1-5)': "meaning",
    'Poeticness (1-5)': "poeticness",
    'Overall (1-5)': "overall",
}
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

with open("data/farewell_saarbrucken.csv", "r") as f:
    data = list(csv.DictReader(f))
    data = [{COLUMN_MAP[k]:v for k, v in item.items()} for item in data]

print("Read", len(data), "rows")

for item_i, item in enumerate(data):
    evaluation = evaluate_translation(
        radio_choice=LABEL_REF,
        poem_src=item["src"],
        poem_ref=item["ref"],
        poem_hyp=item["tgt"],
        return_dict=True,
    )
    for feature_key in FEATURE_KEYS:
        data[item_i][feature_key] = evaluation[feature_key]
with open("data/farewell_saarbrucken_f.csv", "w") as f:
    f = csv.DictWriter(f, fieldnames=data[0].keys())
    f.writeheader()
    f.writerows(data)
