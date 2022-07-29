#!/usr/bin/env python3
import glob
import json
import tqdm

lines = 0
poems = 0
for f in tqdm.tqdm(glob.glob("../corpusCzechVerse/ccv/*.json")):
    with open(f, "r") as f:
        data = json.load(f)
        for poem in data:
            poems += 1
            for stanza in poem["body"]:
                lines += len(stanza)

print(lines, "lines")
print(poems, "poems")