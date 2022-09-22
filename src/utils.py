import json
import os
import io
import sys
import toml

def create_crawl_dir():
    if not os.path.exists('crawl'):
        os.makedirs('crawl')


def json_dump(filename, obj, indent=2):
    with open(filename, "w") as f:
        json.dump(obj, f, indent=indent, ensure_ascii=False)

def json_dumpl(filename, obj):
    with open(filename, "w") as f:
        for l in obj:
            f.write(json.dumps(l, ensure_ascii=False) + "\n")

def json_dumpa(filename, obj, flush=False):
    with open(filename, "a") as f:
        json.dump(obj, f, indent=None, ensure_ascii=False)
        f.write("\n")
        if flush:
            f.flush()


def json_readl(filename):
    with open(filename, "r") as f:
        data = [json.loads(x) for x in f.readlines()]
    return data


def json_read(filename):
    with open(filename, "r") as f:
        return json.load(f)


def delete_file(filename):
    if os.path.exists(filename):
        os.remove(filename)

def _dump_str_prefer_multiline(v):
  multilines = v.split('\n')
  if len(multilines) > 1:
    return toml.encoder.unicode('"""\n' + v.replace('"""', '\\"""').strip() + '\n"""')
  else:
    return toml.encoder._dump_str(v)


class MultilineTomlEncoder(toml.TomlEncoder):
  def __init__(self, _dict=dict, preserve=False):
    super(MultilineTomlEncoder, self).__init__(_dict=dict, preserve=preserve)
    self.dump_funcs[str] = _dump_str_prefer_multiline