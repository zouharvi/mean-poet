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
from utils import json_dumpa, delete_file, create_crawl_dir, json_readl
from crawl.utils_lang import safe_langdetect


def sanitize_url(url):
    url = list(urllib.parse.urlsplit(url))
    url[2] = urllib.parse.quote(url[2])
    url = urllib.parse.urlunsplit(url)
    return url


def process_poem_body(find_all_result):
    """
    Returns the poem text.
    """
    if any([len(line.contents) == 0 for line in find_all_result]):
        return None
    body_raw = [str(line.contents[0]) for line in find_all_result]
    poem = []
    stanza = []
    for line in body_raw:
        # whitespace, break stanza
        if line == "\xa0" and len(stanza) > 0:
            poem.append(stanza)
            stanza = []
        else:
            stanza.append(line.replace("\n", ""))

    if len(stanza) > 0:
        poem.append(stanza)

    return poem


def url_to_poem(url):
    """
    Returns a poem dictionary given PTC target url. May throw errors if anything goes wrong. 
    """
    # get main page
    conn = urllib.request.urlopen(sanitize_url(url))
    html = conn.read()
    soup = BeautifulSoup(html, features="lxml")

    body = soup.find("section", {"class": "poemBody"})
    title_tgt = body.find('h1')
    if title_tgt is None:
        raise Exception("Could not find title tgt")
    if len(title_tgt.contents) == 0:
        raise Exception("Could not find title tgt")
    title_tgt = str(title_tgt.contents[0]).strip('"').replace("\n", "")
    poem_tgt = process_poem_body(body.find_all('div'))
    if poem_tgt is None:
        raise Exception("Could not find poem tgt")

    link_src = url + "/original"
    # get original page
    conn = urllib.request.urlopen(sanitize_url(link_src))
    html = conn.read()
    soup = BeautifulSoup(html, features="lxml")
    body = soup.find("section", {"class": "poemBody"})
    title_src = body.find('h1')
    if title_src is None:
        raise Exception("Could not find title src")
    if len(title_src.contents) == 0:
        raise Exception("Could not find poem src")
    title_src = str(title_src.contents[0]).strip('"').replace("\n", "")
    poem_src = process_poem_body(body.find_all('div'))
    if poem_src is None:
        raise Exception("Could not find poem src")

    body = soup.find("section", {"class": "poemCredits"})
    people = [str(x.contents[0]) for x in body.find_all("a")]

    # apply unified formatting (stanzas separated with an empty lines)
    poem_tgt = "\n\n".join(["\n".join(stanza) for stanza in poem_tgt])
    poem_src = "\n\n".join(["\n".join(stanza) for stanza in poem_src])

    poem = {
        "origin": "ptc",
        "title_tgt": title_tgt,
        "title_src": title_src,
        "author": str(people[0]),
        "translator": ", ".join(people[1:]),
        "year": "",
        "lang_tgt": safe_langdetect(poem_tgt),
        "lang_src": safe_langdetect(poem_src),
        "url": url,
        "poem_tgt": poem_tgt,
        "poem_src": poem_src,
    }
    return poem


def get_all():
    # remove previous iteration if exists
    delete_file("crawl/ptc_txt.jsonl")
    delete_file("crawl/ptc_meta.jsonl")

    print("Phase 1: collecting links")
    poem_urls = []
    # iterate until page 50 (may increase later)
    for page in tqdm(range(1, 51)):
        # get main page
        url = f'https://www.poetrytranslation.org/poems/p{page}'
        conn = urllib.request.urlopen(url)
        html = conn.read()

        soup = BeautifulSoup(html, features="lxml")
        links = soup.find_all('a')

        # extract author links like /andrei-bely/
        links = [tag.get("href", None) for tag in links]
        links = [
            tag for tag in links
            if tag is not None
            and tag.startswith("https://www.poetrytranslation.org/poems/")
            and not re.match(r"^.*/poems/p[0-9]+$", tag)
        ]
        poem_urls += links

        # throttle to not trigger ip limits
        time.sleep(1.1)

    print("Phase 2: downloading actual poems")
    poem_id = 0
    for link_tgt in tqdm(poem_urls):
        try:
            poem = url_to_poem(link_tgt)
        except:
            # skip invalid entries
            continue

        # add id (at the first position)
        poem = {"id": poem_id} | poem
        poem_id += 1

        # continually append poems
        json_dumpa("crawl/ptc_txt.jsonl", poem, flush=True)

        # create stripped-down version for metadata
        del poem["poem_src"]
        del poem["poem_tgt"]
        json_dumpa("crawl/ptc_meta.jsonl", poem, flush=True)

        # throttle to not trigger ip limits
        time.sleep(1.1)


def get_comparable(metadata):
    # remove previous iteration if exists
    delete_file("crawl/ptc_txt.jsonl")

    print("Downloading actual poems")
    for poem_m in tqdm(metadata):
        try:
            poem = url_to_poem(poem_m["url"])
            # add only the content
            poem_m["poem_src"] = poem["poem_src"]
            poem_m["poem_tgt"] = poem["poem_tgt"]
        except:
            # skip invalid entries
            continue

        # continually append poems
        json_dumpa("crawl/ptc_txt.jsonl", poem_m)

        # throttle to not trigger ip limits
        time.sleep(1.1)


if __name__ == "__main__":
    create_crawl_dir()
    args = argparse.ArgumentParser()
    args.add_argument("--metadata", default="crawl/metadata.jsonl")
    args = args.parse_args()

    if len(args.metadata) == 0 or not Path(args.metadata).is_file():
        print("WARNING: Metadata not loaded, crawling anew. Resulting dataset won't be compatible.")
        get_all()
    else:
        metadata = [poem for poem in json_readl(
            args.metadata) if poem["origin"] == "ptc"]
        get_comparable(metadata)
