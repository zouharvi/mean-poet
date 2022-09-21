#!/usr/bin/env python3

import collections
import sys
sys.path.append("src")
from utils import json_read
import numpy as np

data = json_read("data_annotations/parsed.json")

data_docs = collections.defaultdict(list)

for doc_user in data:
    data_docs[doc_user["poem_i"]].append(doc_user["lines"])

categories = ["meaning", "poeticness", "overall"]
rating_pairs = {k:[] for k in categories}

rating_systems = collections.defaultdict(lambda: collections.defaultdict(list))

for docs in data_docs.values():
    for r1, r2 in zip(docs[0], docs[1]):
        for (r1n, r1v), (r2n, r2v) in zip(r1.items(), r2.items()):
            # assume they are sorted the same way (they are *FOR NOW*)
            assert r1n == r2n
            for category in categories:
                v1 = r1v["rating"][category]
                v2 = r2v["rating"][category]
                if v1 is None or v2 is None:
                    continue
                rating_pairs[category].append((
                    v1, v2
                ))
                rating_systems[category][r1v["translator_level"]].append(v1)
                rating_systems[category][r2v["translator_level"]].append(v2)

for category in categories:
    arr_pairs = np.array(rating_pairs[category])
    corr = np.corrcoef(arr_pairs.T)
    print(f"{category:>15}: {corr[0,1]:.2%}")

for category in categories:
    for translator_level, v in rating_systems[category].items():
        print(f"{category:>10} - {translator_level:<15} {np.average(v):.1f}")
    print()