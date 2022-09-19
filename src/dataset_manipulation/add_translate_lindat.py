#!/usr/bin/env python3

import tqdm
import time
import requests
import json
import argparse

def translate_title(poem):
    req = requests.post(
        "https://lindat.cz/services/translation/api/v2/languages/",
        data={"src": poem["lang"], "tgt": "en", "input_text": poem["title"]}
    )
    poem_hyp_title = req.content.decode("utf-8").strip()
    return poem_hyp_title

def translate_full(poem):
    req = requests.post(
        "https://lindat.cz/services/translation/api/v2/languages/",
        data={"src": poem["lang"], "tgt": "en", "input_text": poem["poem"]}
    )
    poem_hyp = req.content.decode("utf-8").strip()

    return poem_hyp

def translate_lines(poem):
    output_lines = []
    for line in poem["poem"].split("\n"):
        if len(line.strip()) == 0:
            output_lines.append("")
        else:
            req = requests.post(
                "https://lindat.cz/services/translation/api/v2/languages/",
                data={"src": poem["lang"], "tgt": "en", "input_text": line}
            )
            line_hyp = req.content.decode("utf-8").strip()
            output_lines.append(line_hyp)

    return "\n".join(output_lines)

def translate_stanzas(poem):
    output_stanzas = []
    for stanza in poem["poem"].split("\n\n"):
        if len(stanza.strip()) == 0:
            output_stanzas.append("")
        else:
            req = requests.post(
                "https://lindat.cz/services/translation/api/v2/languages/",
                data={"src": poem["lang"], "tgt": "en", "input_text": stanza}
            )
            stanza_hyp = req.content.decode("utf-8").strip()
            output_stanzas.append(stanza_hyp)

    return "\n\n".join(output_stanzas)

RECIPES = [
    # ("LINDAT full", translate_full),
    # ("LINDAT lines", translate_lines),
    ("LINDAT stanzas", translate_stanzas),
]

ALLOWED = {"cs", "de"}

if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument(
        "-i", "--input", default="computed/dataset.jsonl",
        help="Path to dataset file"
    )
    args.add_argument(
        "-o", "--output", default="computed/dataset_t0.jsonl",
        help="Path to dataset file"
    )
    args = args.parse_args()

    with open(args.input, "r") as f:
        data = [json.loads(x) for x in f.readlines()]

    for poem_i, poem in enumerate(tqdm.tqdm(data)):
        print("Translating", poem["author"], "-", poem["title"])
        if poem["lang"] not in ALLOWED:
            continue
        
        last_t_key = len([x for x in poem.keys() if "translation-" in x])
        poem_hyp_title = translate_title(poem)

        for extra_i, (mt_name, func) in enumerate(RECIPES):
            poem_hyp = func(poem)
            print(f" - {mt_name} - {poem_hyp_title}")

            # mutate original data
            data[poem_i][f"translation-{extra_i+last_t_key+1}"] = {
                "translator": mt_name,
                "title": poem_hyp_title,
                "translator_level": "machine",
                "poem": poem_hyp
            }

            # throttle request to not overload the server
            time.sleep(0.5)

        # constantly overwrite
        with open(args.output, "w") as f:
            f.writelines([json.dumps(x, ensure_ascii=False) + "\n" for x in data])
