#!/usr/bin/env python3
# import easyocr
from PIL import Image
import urllib.request
import toml, os
from bs4 import BeautifulSoup, NavigableString
import sys
import shutil

# sys.path.append("src")
absolute_path = "/Users/eleanorjiang/Library/Mobile Documents/com~apple~CloudDocs/RESEARCH/PROJECTS/POET/mean-poet/data_raw/chinese_poem"


def process_body(body_list):
    poem = []
    for item in body_list:
        if not isinstance(item, NavigableString):
            continue
        line = str(item).replace("\n", "")
        poem.append(line)
    return poem


def poem_to_toml(poem, save_file):
    with open(save_file, "w") as toml_file:
        toml.dump(poem, toml_file)


def read_img(img_address):
    # "http://chinese-poems.com/li2.png"
    reader = easyocr.Reader(['ch_sim'])
    result = reader.readtext(img_address)
    lines = []
    for i, content in enumerate(result):
        line = content[1].replace(",", "").strip()
        if i % 2 == 0:
            lines.append(line)
    return lines

def extract_peom(author_name, shortcut):
    author = author_name # "Li Bai"
    folder = shortcut  # "lbe"
    url = f'http://chinese-poems.com/{folder}.html'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0',
    }
    r = urllib.request.Request(url, headers=headers)
    html = urllib.request.urlopen(r)
    soup = BeautifulSoup(html, features="lxml")
    links = soup.find_all('a')
    poems = []
    for link in links:
        suffix = link.get('href')[:-5]
        if suffix == "index":
            continue
        url = "http://chinese-poems.com/{}.html".format(suffix)
        r = urllib.request.Request(url, headers=headers)
        html = urllib.request.urlopen(r)
        soup = BeautifulSoup(html, features="lxml")
        title = str(soup.title.string)
        # author = str(soup.find("span", {"class": "poet"}).contents[0])
        if soup.find(id="characters"):
            characters = soup.find(id="characters").contents
            poem_src = process_body(characters)
            translation = soup.find(id="translation").contents
            poem_tgt = process_body(translation)
        else:
            print(url, " has no Chinese text, please check this link manually.")
            # todo： orc
            ## img_address = soup.find_all("img")[0].attrs['src']
            img_address = f"http://chinese-poems.com/{suffix}.gif"
            r = urllib.request.Request(img_address, headers=headers)
            file_name = f"{absolute_path}/{folder}/{suffix}.gif"
            with urllib.request.urlopen(r) as response, open(file_name, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)
            im = Image.open(file_name)
            current = im.tell()
            png_name = f"{absolute_path}/{folder}/{suffix}.png"
            im.save(png_name)
            poem_src = read_img(png_name)
            # poem_src = ["", ""]
            translation = soup.find_all("td")[1]
            translation = translation.contents
            poem_tgt = process_body(translation)
        poem = {
            "title": poem_src[0],
            "author": author,
            "lang": "zh",
            "year": 742,
            "poem": "\n".join(poem_src[1:]),
            "url": url,
            "translation-1": {
                "title": title,
                "translator": "chinese-poem",
                "translator_level": "professional",
                "poem": "\n".join(poem_tgt)
            },
        }
        if not os.path.isdir(f"{absolute_path}/{folder}"):
            os.mkdir(f"{absolute_path}/{folder}")
        save_file = f"{absolute_path}/{folder}/{suffix}.toml"
        poem_to_toml(poem, save_file)


if __name__ == "__main__":
    extract_peom("Li Shangyin", "lie")