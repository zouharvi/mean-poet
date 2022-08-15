#!/usr/bin/env python3

import sys
sys.path.append("src")
from utils import json_reada
from collections import Counter
import argparse

if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("--data", default="crawl/ruverses_txt.jsonl")
    args = args.parse_args()

    lang_dist_src = Counter()
    lang_dist_tgt = Counter()
    lang_dist = Counter()
    lines_src = 0
    lines_tgt = 0

    data = json_reada(args.data)
    print("Loaded", len(data), "poems")

    for poem in data:
        lang_dist_src[poem["lang_src"]] += 1
        lang_dist_tgt[poem["lang_tgt"]] += 1
        lang_dist[(poem["lang_src"], poem["lang_tgt"])] += 1
        lines_src += poem["poem_src"].count("\n") - \
            poem["poem_src"].count("\n\n")
        lines_tgt += poem["poem_tgt"].count("\n") - \
            poem["poem_tgt"].count("\n\n")

    print("SRC language distribution", lang_dist_src)
    print("TGT language distribution", lang_dist_tgt)
    print("Language pair distribution", lang_dist)
    print("SRC lines", lines_src)
    print("TGT lines", lines_tgt)

    for (lang_src, lang_tgt), val in lang_dist.items():
        print(f"{lang_src} [{val}] {lang_tgt}")
