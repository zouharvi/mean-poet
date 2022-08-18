#!/usr/bin/env python3
import sys
sys.path.append("src")
import glob
import toml
import pathlib
from utils import MultilineTomlEncoder

tomlencoder = MultilineTomlEncoder()

for f in glob.glob("data_raw/chs_poem_old/*.toml"):
    fpath = pathlib.Path(f)
    url = "http://www.chinese-poems.com/" + fpath.stem + ".html"
    print(url)
    with open(f, "r") as f:
        data = toml.load(f)
        # add url before the poem
        poem = data["translation-1"].pop("poem")
        data["translation-1"]["url"] = url
        data["translation-1"]["poem"] = poem

    with open(f"data_raw/chs_poem/{fpath.stem}.toml", "w") as f:
        data = toml.dump(data, f, encoder=tomlencoder)