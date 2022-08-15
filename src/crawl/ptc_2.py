#!/usr/bin/env python3

import urllib.request
from bs4 import BeautifulSoup
from tqdm import tqdm
import sys
import time
sys.path.append("src")
from utils import json_read, json_dumpa, delete_file

links = json_read("crawl/ptc_links.json")


def sanitize_url(url):
    url = list(urllib.parse.urlsplit(url))
    url[2] = urllib.parse.quote(url[2])
    url = urllib.parse.urlunsplit(url)
    return url


def process_poem_body(find_all_result):
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


if __name__ == "__main__":
    # remove previous iteration if exists
    delete_file("crawl/ptc_txt.jsonl")

    poems = []
    for link_tgt in tqdm(links):
        print(link_tgt)
        link_src = link_tgt + "/original"

        # get main page
        conn = urllib.request.urlopen(sanitize_url(link_tgt))
        html = conn.read()
        soup = BeautifulSoup(html, features="lxml")
        body = soup.find("section", {"class": "poemBody"})
        title_tgt = body.find('h1')
        if title_tgt is None:
            continue
        if len(title_tgt.contents) == 0:
            continue
        title_tgt = str(title_tgt.contents[0]).strip('"').replace("\n", "")
        poem_tgt = process_poem_body(body.find_all('div'))
        if poem_tgt is None:
            continue

        # get original page
        conn = urllib.request.urlopen(sanitize_url(link_src))
        html = conn.read()
        soup = BeautifulSoup(html, features="lxml")
        body = soup.find("section", {"class": "poemBody"})
        title_src = body.find('h1')
        if title_src is None:
            continue
        if len(title_src.contents) == 0:
            continue
        title_src = str(title_src.contents[0]).strip('"').replace("\n", "")
        poem_src = process_poem_body(body.find_all('div'))
        if poem_src is None:
            continue

        body = soup.find("section", {"class": "poemCredits"})
        people = [str(x.contents[0]) for x in body.find_all("a")]

        poems.append({
            "author_tgt": people[0],
            "poem_tgt": poem_tgt,
            "title_tgt": title_tgt,
            "author_src": "",
            "poem_src": poem_src,
            "title_src": title_src,
            "translated": ", ".join(people[1:]),
            "url": link_tgt,
        })

        # continually append poems
        json_dumpa("crawl/ptc_txt.jsonl", poems[-1])

        time.sleep(1.1)
