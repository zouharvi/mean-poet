#!/usr/bin/env python3

import argparse
from pathlib import Path
import re
import urllib.request
from bs4 import BeautifulSoup
from tqdm import tqdm
import sys
import time
sys.path.append("src")
from utils import json_dumpa, delete_file, create_crawl_dir, json_reada
from crawl.utils_lang import safe_langdetect

def process_poem_body(find_all_result):
    pass

def url_to_poem(url):
    pass


def get_all():
    # remove previous iteration if exists
    delete_file("crawl/lyrikline_txt.jsonl")
    delete_file("crawl/lyrikline_meta.jsonl")

    print("Phase 1: collecting links")

    for lang in ["cs", "de", "zh", "es", "it", "ru", "ar"]:
        pass

        # throttle to not trigger ip limits
        time.sleep(1.1)

if __name__ == "__main__":
    create_crawl_dir()
    args = argparse.ArgumentParser()
    args.add_argument("--metadata", default="")
    args = args.parse_args()

    if len(args.metadata) == 0 or not Path(args.metadata).is_file():
        print("WARNING: Metadata not loaded, crawling anew. Resulting dataset won't be compatible.")
        get_all()
    else:
        pass