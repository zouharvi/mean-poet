#!/usr/bin/env python3

import argparse
from pathlib import Path
import time
import urllib.request
from bs4 import BeautifulSoup
from tqdm import tqdm
import sys
sys.path.append("src")
from utils import json_dumpa, delete_file, create_crawl_dir, json_reada
from crawl.utils_lang import safe_langdetect

processed_urls = set()


def parse_poem(poem):
    soup = BeautifulSoup(str(poem), features="lxml")
    title_1 = soup.find("h1")
    if title_1 is None:
        title = soup.find("h2").contents
    else:
        title = title_1.contents

    # first is author, then linebreak, then title, then optionally audio
    title = [str(x) for x in title]
    title = [x for x in title if x != "<br/>"]
    if len(title) == 2:
        author = title[0]
        title = title[1]
    else:
        author = ""
        title = ""

    paragraphs = soup.find_all("p")

    poem = []

    # iterate over stanzas
    for paragraph in paragraphs:
        paragraph = [str(line) for line in paragraph.contents]
        poem.append([
            line.strip() for line in paragraph
            if "<br/>" not in line and "<br>" not in line
        ])

    return author, title, poem


def url_to_poem(poem_url):
    """
    Parses a poem given an url and author name.
    Returns either a `list` of target url, a `dict` if a `poem` was parsed or None (if error occured)
    """
    try:
        url = f'https://ruverses.com/{poem_url}'
        conn = urllib.request.urlopen(url)
        html = conn.read()

        soup = BeautifulSoup(html, features="lxml")

        if len(list(soup.find_all("h5"))) == 0:
            # not final poem but a branching website
            links = soup.find_all('a')

            # extract author links like /andrei-bely/
            links = [tag.get("href", None) for tag in links]
            links = [
                tag for tag in links
                if tag is not None and tag.count("/") == 4 and "ruverses.com" not in tag
            ]
            # this is potentially cyclic if the website is
            return links

        poem_tgt = soup.find('div', {'class': 'article'})
        year = soup.find('time').contents[0]
        author_tgt, title_tgt, poem_tgt = parse_poem(poem_tgt)
        poem_src = soup.find('div', {'class': 'original'})
        author_src, title_src, poem_src = parse_poem(poem_src)

        # apply unified formatting (stanzas separated with an empty lines)
        poem_tgt = "\n\n".join(["\n".join(stanza) for stanza in poem_tgt])
        poem_src = "\n\n".join(["\n".join(stanza) for stanza in poem_src])

        # extract translator from the footer
        translator = str(
            soup.find_all('h5')[0].contents[0]
        ).strip().replace("  ", " ")

        poem = {
            "origin": "ruverses",
            "title_tgt": title_tgt,
            "title_src": title_src,
            "author": author_tgt,
            "translator": translator,
            "year": year,
            "lang_tgt": safe_langdetect(poem_tgt),
            "lang_src": safe_langdetect(poem_src),
            "url": url,
            "poem_tgt": poem_tgt,
            "poem_src": poem_src,
        }
        return poem
    except Exception as e:
        print(e)
        pass


def get_all():
    # remove previous iteration if exists
    delete_file("crawl/ruverses_txt.jsonl")
    delete_file("crawl/ruverses_meta.jsonl")

    print("Phase 1: collecting links")
    # get main page
    url = 'https://ruverses.com/'
    conn = urllib.request.urlopen(url)
    html = conn.read()

    soup = BeautifulSoup(html, features="lxml")
    links = soup.find_all('a')

    # extract author links like /andrei-bely/
    links = [tag.get("href", None) for tag in links]
    links = [tag for tag in links if tag is not None and tag.count("/") == 2]

    poem_urls = []
    for author in tqdm(links):
        url = f"https://ruverses.com{author}"
        conn = urllib.request.urlopen(url)
        html = conn.read()
        soup = BeautifulSoup(html, features="lxml")
        links = soup.find_all('a')

        # extract poem links like /georgy-adamovich/a-window-a-dawn/
        links = [tag.get("href", None) for tag in links]
        links = [
            tag
            for tag in links
            if tag is not None and tag.count("/") == 3 and "ruverses.com" not in tag
        ]

        author = author.replace("-", " ").replace("/", "").title()

        poem_urls += links

        # throttle to not trigger ip limits
        time.sleep(1.1)

    processed_urls = set()
    poem_id = 0
    print("Phase 2: Following direct links")
    # maximum iteration limit is 20
    # normally it should stop around ~5th iteration
    for i in range(20):
        print("- Iteration", i + 1)
        poem_urls_next = []

        for poem_url in tqdm(poem_urls):
            # make sure that we don't collect anything twice
            # (it's necessary because one batch can contain multiple)
            if poem_url in processed_urls:
                continue
            processed_urls.add(poem_url)

            output = url_to_poem(poem_url)
            # the function signature is messy but it's either a list of author-url tuples or the poem
            if type(output) is list:
                poem_urls_next += output
            elif type(output) is dict:
                poem = output
                # add id (at the first position)
                poem = {"id": poem_id} | poem
                # sometimes the result is not perfectly serializable and throws an error
                # in that case, skip it
                try:
                    json_dumpa("crawl/ruverses_txt.jsonl", poem, flush=True)

                    # create stripped-down version for metadata
                    del poem["poem_src"]
                    del poem["poem_tgt"]
                    json_dumpa("crawl/ruverses_meta.jsonl", poem, flush=True)
                    poem_id += 1
                except:
                    pass
            # sleep for 0.2 seconds to not overrun the server
            # lowers from 4 it/s to 3 it/s
            time.sleep(0.2)

        # go to the next iteration
        poem_urls = [
            url for url in poem_urls_next
            if url not in processed_urls
        ]

        if len(poem_urls) == 0:
            break


def get_comparable(metadata):
    # remove previous iteration if exists
    delete_file("crawl/ruverses_txt.jsonl")

    print("Downloading actual poems")
    for poem_m in tqdm(metadata):
        output = url_to_poem(poem_m["url"])
        # the function signature is messy but it's either a list of author-url tuples or the poem
        if type(output) is list or output is None:
            continue

        poem = output
        poem_m["poem_src"] = poem["poem_src"]
        poem_m["poem_tgt"] = poem["poem_tgt"]
        # continually append
        json_dumpa("crawl/ruverses_txt.jsonl", poem_m, flush=True)

        # sleep for 0.2 seconds to not overrun the server
        # lowers from 4 it/s to 3 it/s
        time.sleep(0.2)


if __name__ == "__main__":
    create_crawl_dir()

    args = argparse.ArgumentParser()
    args.add_argument("--metadata", default="crawl/metadata.jsonl")
    args = args.parse_args()

    if len(args.metadata) == 0 or not Path(args.metadata).is_file():
        print("WARNING: Metadata not loaded, crawling anew. Resulting dataset won't be compatible.")
        get_all()
    else:
        metadata = [
            poem for poem
            in json_reada(args.metadata)
            if poem["origin"] == "ruverses"
        ]
        get_comparable(metadata)
