#!/usr/bin/env python3

import sys
sys.path.append("src")
from utils import json_reada, json_dumpa, delete_file
import langdetect
from collections import Counter
from tqdm import tqdm
import argparse

def safe_langdetect(poem):
    try:
        return langdetect.detect(poem)
    except langdetect.lang_detect_exception.LangDetectException as e:
        return "??"

def process_poem(poem):
    text_src = "\n".join(["\n".join(stanza) for stanza in poem["poem_src"]])+poem["title_src"]
    text_tgt = "\n".join(["\n".join(stanza) for stanza in poem["poem_tgt"]])+poem["title_tgt"]

    poem["lang_src"] = safe_langdetect(text_src)
    poem["lang_tgt"] = safe_langdetect(text_tgt)
    return poem

if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument(
        "--sankey", action="store_true",
        help="Generate input to https://www.sankeymatic.com/"
    )
    args.add_argument(
        "--data",
        default="crawl/ruverses_txt_langs.jsonl",
    )
    args = args.parse_args()
    
    delete_file("crawl/ruverses_txt_langs.jsonl")
    
    lang_dist_src = Counter()
    lang_dist_tgt = Counter()
    lang_dist = Counter()
    lines_src = 0

    data = json_reada(args.data)
    print("Loaded", len(data), "poems")

    for poem in tqdm(data):
        poem = process_poem(poem)
        lang_dist_src[poem["lang_src"]] += 1
        lang_dist_tgt[poem["lang_tgt"]] += 1
        lang_dist[(poem["lang_src"], poem["lang_tgt"])] += 1
        json_dumpa("crawl/ruverses_txt_langs.jsonl", poem)
        lines_src += sum([stanza.count("\n") + 1 for stanza in poem["poem_src"]])

    print("SRC language distribution", lang_dist_src)
    print("TGT language distribution", lang_dist_tgt)
    print("Language pair distribution", lang_dist)
    print("SRC lines", lines_src)

    if args.sankey:
        for (lang_src, lang_tgt), val in lang_dist.items():
            print(f"{lang_src} [{val}] {lang_tgt}")