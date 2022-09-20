#!/usr/bin/env python3

import argparse
from pathlib import Path
import re
import urllib.request
from bs4 import BeautifulSoup
from tqdm import tqdm
import sys
import time
import re, os, toml
sys.path.append("src")
# from utils import json_dumpa, delete_file, create_crawl_dir, json_reada
#from crawl.utils_lang import safe_langdetect

HEADER = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0', }
absolute_path = "/Users/eleanorjiang/iCloud/RESEARCH/PROJECTS/POET/mean-poet/data_raw/lyrikline"

LANG_MAP = {"german": "de", "english": "en", "chinese": "zh", }

def poem_to_toml(poem, save_file):
    with open(save_file, "w") as toml_file:
        toml.dump(poem, toml_file)


def get_soup(url):
    html = urllib.request.urlopen(urllib.request.Request(url, headers=HEADER))
    soup = BeautifulSoup(html, features="lxml")
    return soup


def strip_text(text):
    return text.strip("\n").strip(" ").replace("\xa0", " ").replace("\xa0", " ")

def process_poem(div, lang="src"):
    title, poem_str, meta_info = "", "", ""
    for content in div.contents:
        if hasattr(content, "attrs") and "class" in content.attrs.keys():
            if (content.attrs["class"] == ['title']):
                title = strip_text(content.text)
            elif ('poem-text' in content.attrs["class"]) and len(content.contents) > 0:
                poem_tag = content.contents[0]
                poem_lines = [strip_text(str(content)) for content in poem_tag.contents]
                poem_str = "".join(poem_lines).replace("<br/>", "\n")
            elif (content.attrs["class"] == ['foot']):
                meta_info = strip_text(content.text)
    # text = strip_text(div.text)
    # lines = text.split("\n")
    # lines = [strip_text(line) for line in lines]
    # title = lines[0]
    # poem_lines = lines[1:-1]
    # meta_info = lines[-1]
    # if poem_lines[0] == "":
    #     poem_lines = poem_lines[1:]
    if lang == "src":
        year = re.search(r"\d{4,4}", meta_info)
        if year:
            year = year.group()
        else:
            year = ""
        meta_info = year
    else:
        translator = " ".join(meta_info.split(" ")[-2:])
        meta_info = translator
    return title, poem_str, meta_info

def get_meta_info(contents):
    for content in contents:
        if hasattr(content, "attrs"):
            if "class" in content.attrs.keys() and content.attrs["class"] == ['lang']:
                lang = strip_text(content.text)
            else:
                name = strip_text(content.text)
    return name, lang


def get_translation(url, author_suffix, save_dir):
    # if url == "https://www.lyrikline.org/en/translations/details/19980/5904":
    #     print("stop")
    author = " ".join(author_suffix.split("-"))
    suffix = "-".join(url.split("/")[-2:])
    soup = get_soup(url)
    mydivs = soup.find_all('div')
    for div in mydivs:
        if "class" in div.attrs.keys():
            if (div.attrs["class"] == ['col-sm-6', 'target-orig']):
                # process peom
                src_title, src_poem_str, year = process_poem(div, lang="src")
                # print(src_title, src_poem_lines)
                if src_poem_str == "":
                   return
            elif (div.attrs["class"] == ['col-sm-6', 'target-tl']):
                # process peom
                div = div.contents[1]
                tgt_title, tgt_poem_str, translator = process_poem(div, lang="tgt")
                # print(tgt_title, tgt_poem_lines)
                if tgt_poem_str == "":
                   return
            elif (div.attrs["class"] == ['transl-name']):
                (translator, tgt_lang) = get_meta_info(div.contents)
            elif (div.attrs["class"] == ['author-name']):
                (author, src_lang) = get_meta_info(div.contents)
    poem = {
        "title": src_title,
        "author": author,
        "lang": src_lang,
        "year": year,
        "poem": src_poem_str,
        "url": url,
        "translation-1": {
            "title": tgt_title,
            "translator": translator,
            "lang": tgt_lang,
            "translator_level": "professional",
            "poem": tgt_poem_str
        }
    }
    suffix = f"{src_lang}-{tgt_lang}-{suffix}"
    if not os.path.isdir(os.path.join(save_dir, author_suffix)):
        os.mkdir(os.path.join(save_dir, author_suffix))
    save_file = f"{save_dir}/{author_suffix}/{suffix}.toml"
    poem_to_toml(poem, save_file)

    return


def get_author(author_suffix, save_dir):
    author_url = f"https://www.lyrikline.org/en/authors/{author_suffix}"
    soup = get_soup(author_url)
    links = soup.find_all('a')
    for link in links:
        link_line = link.get('href')
        if link_line:
            peom_url = re.search(r"https://www.lyrikline.org/en/translations/details/\d*/\d*", link_line)
            if peom_url:
                peom_url = peom_url.group()
                get_translation(peom_url, author_suffix, save_dir=save_dir)
    return


def get_lang(author_search_url, save_dir, exclude=[]):
    soup = get_soup(author_search_url)
    links = soup.find_all('a')
    for link in links:
        link_line = link.get('href')
        if link_line:
            author_url = re.search(r"/en/authors/\S+", link_line)
            if author_url:
                author_suffix = author_url.group().split("/")[-1]
                if author_suffix not in exclude:
                    print(f"getting {author_suffix}...")
                    get_author(author_suffix, save_dir=save_dir)
                    print(f"done.")
    return



if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("--save_dir", default="lyrikline",
                      help="If not given, a folder named with `lyrikline` would be created in the current directory.")
    args.add_argument("-l", "--lang", type=str, nargs="+", required=True,
                       help="language shortcut(s), for example, zh")
    args.add_argument("-e", "--exclude-list", type=str, nargs="+", default=[],
                       help="exclude author suffix(es)")
    args = args.parse_args()
    if args.save_dir == "":
        args.save_dir = "lyrikline"
    if not os.path.isdir(args.save_dir):
        os.mkdir(args.save_dir)
    for lang in args.lang:
        lang_save_dir = f"{args.save_dir}/{lang}"
        if not os.path.isdir(lang_save_dir):
            os.mkdir(lang_save_dir)
        author_search_url = f"https://www.lyrikline.org/en/authors?nav=1&lang%5B%5D={lang}"
        # exclude = ["bei-dao", "bei-ling"]
        get_lang(author_search_url, save_dir=lang_save_dir, exclude=args.exclude_list)
