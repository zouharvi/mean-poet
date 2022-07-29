#!/usr/bin/env python3

import urllib
from bs4 import BeautifulSoup
from tqdm import tqdm
import json
import sys
sys.path.append("src")
from utils import json_dumpa, delete_file

poems_text = []
poem_tuples_extra = []
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
        # print last stanza
        # print("\n".join(poem[-1]))
        # print("/")

    return author, title, poem


errors = []


def process_poem_tuples(poem_tuples):
    global poem_tuples_extra, errors

    for poem_tuple in tqdm(poem_tuples):
        author, poem_url = poem_tuple
        # print("Processing", poem_url)

        if poem_url in processed_urls:
            continue
        
        processed_urls.add(poem_url)

        try:
            url = f'https://ruverses.com/{poem_url}'
            conn = urllib.request.urlopen(url)
            html = conn.read()

            soup = BeautifulSoup(html, features="lxml")

            if len(list(soup.find_all("h5"))) == 0:
                # not final poem
                links = soup.find_all('a')

                # extract author links like /andrei-bely/
                links = [tag.get("href", None) for tag in links]
                links = [
                    tag for tag in links
                    if tag is not None and tag.count("/") == 4 and "ruverses.com" not in tag
                ]
                # print("Adding", [(author, tag) for tag in links])
                # this is potentially cyclic if the website is
                poem_tuples_extra += [(author, tag) for tag in links]
                # print("Skipping & adding", links, "\n")

                # skip this page
                continue

            poem_tgt = soup.find('div', {'class': 'article'})
            author_tgt, title_tgt, poem_tgt = parse_poem(poem_tgt)
            poem_src = soup.find('div', {'class': 'original'})
            author_src, title_src, poem_src = parse_poem(poem_src)

            # extract translator from the footer
            translator = str(soup.find_all(
                'h5')[0].contents[0]).strip().replace("  ", " ")
            # print("Translated by", translator)

            poems_text.append({
                "author_tgt": author_tgt,
                "poem_tgt": poem_tgt,
                "title_tgt": title_tgt,
                "author_src": author_src,
                "poem_src": poem_src,
                "title_src": title_src,
                "translated": translator,
                "url": url,
            })

            # continually append
            json_dumpa("crawl/ruverses_txt.jsonl", poems_text[-1])

            # sleep for 0.2 seconds to not overrun the server
            # lowers from 4 it/s to
            # time.sleep(0.2)
        except Exception as e:
            errors.append(e)


if __name__ == "__main__":
    # remove previous iteration if exists
    delete_file("crawl/ruverses_txt.jsonl")

    with open("crawl/ruverses_links.json", "r") as f:
        poem_tuples = json.load(f)

    print("Following direct links")
    process_poem_tuples(poem_tuples)
    print("Crawled (sub)total", len(poems_text), "poems")

    print("Following leftover direct links")
    process_poem_tuples(poem_tuples_extra)
    print("Crawled total", len(poems_text), "poems")

    print("With", len(errors), "errors")
    with open("crawl/ruverses_errors.txt", "w") as f:
        for e in errors:
            print(e, file=f)
