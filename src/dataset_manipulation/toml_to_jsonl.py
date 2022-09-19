#!/usr/bin/env python3

import glob
import toml
import json
import pathlib
import argparse
import collections

args = argparse.ArgumentParser(
    usage="Processes all data_raw/*.toml files and starts a new jsonl dataset file"
)
args.add_argument(
    "--overwrite", action="store_true",
    help="Overwrite target dataset if exists"
)
args.add_argument("-i", "--input", nargs="+", default=[
    "data_raw/chs_poem/*.toml", "data_raw/lyrikline/*.toml", 
    "data_raw/other/*.toml", "data_raw/wikics/*.toml", 
])
args.add_argument("-o", "--output", default="computed/dataset.jsonl")
args = args.parse_args()

if pathlib.Path(args.output).is_file():
    print(args.output, "already exists")
    if not args.overwrite:
        print("Terminating because you did not specify --overwrite")
        exit()

# clear file otherwise
with open(args.output, "w") as f:
    f.write("")

langs = []

count_poem_tgt = 0
count_poem_src = 0
count_stanza_src = 0

all_files = [f for glob_path in args.input for f in glob.glob(glob_path)]
for f in all_files:
    print("Reading", f)
    with open(f, "r") as f:
        poem = toml.load(f)
    count_poem_src += 1

    langs.append(poem["lang"])

    t_keys = [key_t for key_t in poem.keys() if "translation-" in key_t]
    
    count_stanza_src += poem["poem"].count("\n\n") + 1
    count_poem_tgt += len(t_keys)

    with open(args.output, "a") as ft:
        json.dump(poem, ft, ensure_ascii=False)
        ft.write("\n")
        ft.flush()

print(f"{count_poem_src:>5} src poems in total")
print(f"{count_poem_tgt:>5} tgt poems in total")
print(f"{count_stanza_src:>5} src stanzas in total")
print(collections.Counter(langs))