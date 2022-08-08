#!/usr/bin/env python3

import toml
import json
import argparse

def _dump_str_prefer_multiline(v):
  multilines = v.split('\n')
  if len(multilines) > 1:
    return toml.encoder.unicode('"""\n' + v.replace('"""', '\\"""').strip() + '\n"""')
  else:
    return toml.encoder._dump_str(v)


class MultilinePreferringTomlEncoder(toml.TomlEncoder):
  def __init__(self, _dict=dict, preserve=False):
    super(MultilinePreferringTomlEncoder, self).__init__(_dict=dict, preserve=preserve)
    self.dump_funcs[str] = _dump_str_prefer_multiline

if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument(
        "-d", "--dataset", default="data_raw/dataset.jsonl",
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

    str_output = toml.dumps(data[0], MultilinePreferringTomlEncoder())

    print(str_output)
