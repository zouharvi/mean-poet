import json
import os

def create_crawl_dir():
    if not os.path.exists('crawl'):
        os.makedirs('crawl')

def json_dump(filename, obj, indent=2):
    with open(filename, "w") as f:
        json.dump(obj, f, indent=indent, ensure_ascii=False)


def json_dumpa(filename, obj):
    with open(filename, "a") as f:
        json.dump(obj, f, indent=None, ensure_ascii=False)
        f.write("\n")


def json_reada(filename):
    with open(filename, "r") as f:
        data = [json.loads(x) for x in f.readlines()]
    return data

def json_read(filename):
    with open(filename, "r") as f:
        return json.load(f)


def delete_file(filename):
    if os.path.exists(filename):
        os.remove(filename)
