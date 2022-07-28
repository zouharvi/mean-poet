#!/usr/bin/env python3

import sys
sys.path.append("src")
from utils import json_reada, json_dumpa, delete_file
import langdetect
from collections import Counter
from tqdm import tqdm

delete_file("crawl/ruverses_txt_langs.jsonl")

def process_poem(poem):
    text_src = "\n".join(["\n".join(stanza) for stanza in poem["poem_src"]])+poem["title_src"]
    poem["lang_src"] = langdetect.detect(text_src)
    text_tgt = "\n".join(["\n".join(stanza) for stanza in poem["poem_tgt"]])+poem["title_tgt"]
    poem["lang_tgt"] = langdetect.detect(text_tgt)
    return poem

if __name__ == "__main__":
    lang_dist_src = Counter()
    lang_dist_tgt = Counter()

    data = json_reada("crawl/ruverses_txt.jsonl")
    print("Loaded", len(data), "poems")

    for poem in tqdm(data):
        poem = process_poem(poem)
        lang_dist_src[poem["lang_src"]] += 1
        lang_dist_tgt[poem["lang_tgt"]] += 1
        json_dumpa("crawl/ruverses_txt_langs.jsonl", poem)

    print("SRC language distribution", lang_dist_src)
    print("TGT language distribution", lang_dist_tgt)