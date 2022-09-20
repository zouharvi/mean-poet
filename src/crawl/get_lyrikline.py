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
# from utils import json_dumpa, delete_file, create_crawl_dir, json_reada
#from crawl.utils_lang import safe_langdetect

def process_poem_body(find_all_result):
    pass

def url_to_poem(url):
    pass

def get_author():
    url = "https://www.lyrikline.org/en/poems/1118-7993"
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0',}
    r = urllib.request.Request(url, headers=headers)
    html = urllib.request.urlopen(r)
    soup = BeautifulSoup(html)
    links = soup.find_all('a')

    print("end")
    return


def get_all():
    # remove previous iteration if exists
    # delete_file("crawl/lyrikline_txt.jsonl")
    # delete_file("crawl/lyrikline_meta.jsonl")

    for lang in ["zh"]:  # ["cs", "de", "zh", "es", "it", "ru", "ar"]
        pass

        # throttle to not trigger ip limits
        time.sleep(1.1)

if __name__ == "__main__":
    get_author()