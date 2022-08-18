#!/usr/bin/env python3

import sys
sys.path.append("src")
import toml
import json
import argparse
from utils import MultilineTomlEncoder


if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument(
        "-d", "--dataset", default="computed/dataset.jsonl",
        help="Path to dataset file"
    )
    args.add_argument(
        "-t", "--title", default="",
    )
    args.add_argument(
        "-a", "--author", default="",
    )
    args = args.parse_args()

    with open(args.dataset, "r") as f:
        data = [json.loads(x) for x in f.readlines()]
        data = [x for x in data if args.title in x["title"].lower() and args.author in x["author"].lower()]

    str_output = toml.dumps(data[0], MultilineTomlEncoder())

    print(str_output)
