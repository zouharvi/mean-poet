#!/usr/bin/env python3

import tqdm
import time
import json
import argparse
from googletrans import Translator
translator = Translator()

def normalize_lang(lang):
    if lang == "zh":
        return "auto"
    else:
        return lang

def translate_title(poem):
    poem_hyp_title = translator.translate(
        poem["title"], dest="en", src=normalize_lang(poem["lang"]),
    ).text
    return poem_hyp_title

def translate_full(poem):
    poem_hyp = translator.translate(
        poem["poem"], dest="en", src=normalize_lang(poem["lang"]),
    ).text

    return poem_hyp

def translate_lines(poem):
    output_lines = []
    for line in poem["poem"].split("\n"):
        if len(line.strip()) == 0:
            output_lines.append("")
        else:
            line_hyp = translator.translate(
                line, dest="en", src=normalize_lang(poem["lang"]),
            ).text
            output_lines.append(line_hyp)

    return "\n".join(output_lines)

def translate_stanzas(poem):
    poem_txt = poem["poem"].replace("\n\n", " [SEP] ")

    poem_hyp = translator.translate(
        poem_txt, dest="en", src=normalize_lang(poem["lang"]),
    ).text

    poem_hyp = poem_hyp.replace(" [SEP] ", "\n\n").replace("[SEP]", "")
    return poem_hyp

RECIPES = [
    # it's lines anyway
    ("Google lines", translate_full),
    # ("Google lines", translate_lines),
    ("Google stanzas", translate_stanzas),
]

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
