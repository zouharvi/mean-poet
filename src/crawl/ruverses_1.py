#!/usr/bin/env python3

import urllib
from bs4 import BeautifulSoup
from tqdm import tqdm
import os
from utils import json_dump

if not os.path.exists('crawl'):
    os.makedirs('crawl')

# get main page
url = 'https://ruverses.com/'
conn = urllib.request.urlopen(url)
html = conn.read()

soup = BeautifulSoup(html, features="lxml")
links = soup.find_all('a')

# extract author links like /andrei-bely/
links = [tag.get("href", None) for tag in links]
links = [tag for tag in links if tag is not None and tag.count("/") == 2]

poems = []


for author in tqdm(links):
    url = f"https://ruverses.com{author}"
    conn = urllib.request.urlopen(url)
    html = conn.read()
    soup = BeautifulSoup(html, features="lxml")
    links = soup.find_all('a')

    # extract poem links like /georgy-adamovich/a-window-a-dawn/
    links = [tag.get("href", None) for tag in links]
    links = [tag for tag in links if tag is not None and tag.count("/") == 3 and "ruverses.com" not in tag]

    author = author.replace("-", " ").replace("/", "").title()

    poems += [
        [author, poem_link]
        for poem_link in links
    ]

    # continually override poems
    json_dump("crawl/ruverses_links.json", poems)