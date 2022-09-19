#!/usr/bin/env python3

import json
import pathlib
import argparse

args = argparse.ArgumentParser()
args.add_argument(
    "--overwrite", action="store_true",
    help="Overwrite target dataset if exists"
)
args.add_argument(
    "--lang-filter", default=None,
    help="Filter specific languages by code (e.g. hi - Hindi)"
)
args.add_argument("-i", "--input", nargs="+", default=[
    "crawl/ptc_txt.jsonl"
])
args.add_argument("-o", "--output", default="computed/dataset_ptc.jsonl")
args = args.parse_args()

if pathlib.Path(args.output).is_file():
    print(args.output, "already exists")
    if not args.overwrite:
        print("Terminating because you did not specify --overwrite")
        exit()

# clear file otherwise
with open(args.output, "w") as f:
    f.write("")

data = []

count_poem = 0

for f in args.input:
    print("Reading", f)
    with open(f, "r") as f:
        data += [json.loads(x) for x in f.readlines()]

for poem in data:
    if args.lang_filter is not None:
        if poem["lang_src"] != args.lang_filter:
            continue

    count_poem += 1

    poem_new = {
        "title": poem["title_src"],
        "author": poem["author"],
        "lang": poem["lang_src"],
        "year": "",
        "poem": poem["poem_src"],
        "translation-1": {
            "title": poem["title_tgt"],
            "translator": poem["translator"],
            # assumption
            "translator_level": "professional",
            "url": poem["url"],
            "poem": poem["poem_tgt"],
        }
    }

    with open(args.output, "a") as ft:
        json.dump(poem_new, ft, ensure_ascii=False)
        ft.write("\n")
        ft.flush()

print(count_poem, "total poems")
