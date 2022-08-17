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
args.add_argument("-i", "--input", nargs="+")
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

count_poem = 0
for f in args.input:
    print("Reading", f)
    with open(f, "r") as f:
        poem = toml.load(f)
        t_keys = [key_t for key_t in poem.keys() if "translation-" in key_t]
        translations = []
        for t_key in t_keys:
            translations.append(poem.pop(t_key))
        
        poem["poem_src"] = poem.pop("poem")
        
        for translation in translations:
            count_poem += 1
            poem_local = poem.copy()
            poem["title_tgt"] = translation["title"]
            poem["poem_tgt"] = translation["poem"]
            poem["translator"] = translation["translator"]

            with open(args.target, "a") as ft:
                json.dump(poem_local, ft, ensure_ascii=False)
                ft.write("\n")
                ft.flush()

print(f"{count_poem:>5} poems in total")