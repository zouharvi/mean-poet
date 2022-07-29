#!/usr/bin/env python3

import urllib
from bs4 import BeautifulSoup
from tqdm import tqdm
import re
import sys
sys.path.append("src")
from utils import json_read

links = json_read("crawl/ptc_links.json")

for link in tqdm(links):
    link_original = link + "/original"
    print(link)
    continue

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
    poems += links

    # continually override poems
    json_dump("crawl/ptc_links.json", poems)
