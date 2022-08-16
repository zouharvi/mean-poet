#!/usr/bin/env python3

import glob
import toml
import json
import pathlib
import argparse

args = argparse.ArgumentParser(
    usage="Processes all data_raw/*.toml files and starts a new jsonl dataset file"
)
args.add_argument(
    "-o", "--overwrite", action="store_true",
    help="Overwrite target dataset if exists"
)
args.add_argument("-t", "--target", default="computed/dataset.jsonl")
args = args.parse_args()

if pathlib.Path(args.target).is_file():
    print(args.target, "already exists")
    if not args.overwrite:
        print("Terminating because you did not specify --overwrite")
        exit()

# clear file otherwise
with open(args.target, "w") as f:
    f.write("")

count_src = 0
count_tgt = 0
count_poem = 0

for f in glob.glob("data_raw/*.toml"):
    print("Reading", f)
    count_poem += 1
    with open(f, "r") as f:
        poem = toml.load(f)
        count_src += len([x for x in poem["poem"].split("\n") if len(x) > 0])
        count_tgt += sum([
            len([x for x in poem[key_t]["poem"].split("\n") if len(x) > 0])
            for key_t in poem.keys() if "translation-" in key_t
        ])

        with open(args.target, "a") as ft:
            json.dump(poem, ft, ensure_ascii=False)
            ft.write("\n")

print(f"{count_poem:>5} poems in total")
print(f"{count_src:>5} src lines in total")
print(f"{count_tgt:>5} tgt lines in total")