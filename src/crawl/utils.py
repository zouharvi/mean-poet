import json


def json_dump(filename, obj):
    with open(filename, "w") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)

def json_dumpa(filename, obj):
    with open(filename, "a") as f:
        json.dump(obj, f, indent=None, ensure_ascii=False)
        f.write("\n")