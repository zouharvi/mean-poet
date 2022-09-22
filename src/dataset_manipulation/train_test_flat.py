#!/usr/bin/env python3

import collections
import sys
sys.path.append("src")
from utils import json_dump, json_dumpa, json_dumpl, json_read
import numpy as np

data = json_read("data_annotations/parsed.json")

data_docs = collections.defaultdict(list)

for doc_user in data:
    # set to a specific user
    # if doc_user["uid"] == "dataset_s0_vilem":
    data_local = []
    for line in doc_user["lines"]:
        line_keys = list(line.keys())
        reference = line[line_keys[0]]
        for line_trans_key in line_keys[1:]:
            line_local = line[line_trans_key]
            line_local["hyp"] = line_local.pop("orig")
            line_local["ref"] = reference["orig"] 
            line_local["translator"] = line_trans_key
            # flatten out the rating
            line_local |= line_local.pop("rating")
            data_local.append(line_local)
    data_docs[doc_user["poem_i"]].append(data_local)

# leave last poem for eval
data_flat_train = [l for docs in list(data_docs.values())[:-1] for doc in docs for l in doc]
data_flat_dev = [l for docs in list(data_docs.values())[-1:] for doc in docs for l in doc]
print(len(data_flat_train), "train lines total")
print(len(data_flat_dev), "dev lines total")

json_dumpl("data_annotations/parsed_flat_train.jsonl", data_flat_train)
json_dumpl("data_annotations/parsed_flat_dev.jsonl", data_flat_dev)
