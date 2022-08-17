import json
import os
import io
import sys


def create_crawl_dir():
    if not os.path.exists('crawl'):
        os.makedirs('crawl')


def json_dump(filename, obj, indent=2):
    with open(filename, "w") as f:
        json.dump(obj, f, indent=indent, ensure_ascii=False)


def json_dumpa(filename, obj, flush=False):
    with open(filename, "a") as f:
        json.dump(obj, f, indent=None, ensure_ascii=False)
        f.write("\n")
        if flush:
            f.flush()


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

class MaskPrint:
    """
    Masks output of prints within its context.
    Is not safe to be nested because it does not have a stack.
    """
    def __init__(self, stderr=True, stdout=True):
        self.stderr = stderr
        self.stdout = stdout

    def __enter__(self):
        # flush before so that it's not affected
        sys.stdout.flush()
        sys.stderr.flush()
        
        if self.stderr:
            sys.stderr = io.StringIO()
        if self.stdout:
            sys.stdout = io.StringIO()

    def __exit__(self, exc_type, exc_val, exc_tb):
        # flush before so that it *is* affected
        sys.stdout.flush()
        sys.stderr.flush()

        if self.stderr:
            sys.stderr = sys.__stderr__
        if self.stdout:
            sys.stdout = sys.__stdout__