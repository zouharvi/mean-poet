#!/usr/bin/env python3

import time
import tqdm
import json
import argparse
import pickle
from googletrans import Translator
translator = Translator()


def translate_full(stanza, src_lang, tgt_lang):
    poem_hyp = translator.translate(
        stanza, dest=tgt_lang, src=src_lang,
    ).text

    return poem_hyp


def translate_lines(poem):
    output_lines = []
    for line in poem["poem"].split("\n"):
        if len(line.strip()) == 0:
            output_lines.append("")
        else:
            line_hyp = translator.translate(
                line, dest="en", src=poem["lang"],
            ).text
            output_lines.append(line_hyp)

    return "\n".join(output_lines)


def paraphrase(stanza):
    return translate_full(
        translate_full(stanza, src_lang="en", tgt_lang="cs"),
        src_lang="cs", tgt_lang="en"
    )


if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument(
        "-d", "--dataset", default="data_raw/dataset.jsonl",
        help="Path to dataset file"
    )
    args.add_argument(
        "-o", "--out", default="data_raw/dataset_class_parap.pkl",
        help="Path to output dataset file"
    )
    args = args.parse_args()

    with open(args.dataset, "r") as f:
        data = [json.loads(x) for x in f.readlines()]

    data_new = []

    for poem_i, poem in enumerate(tqdm.tqdm(data)):
        t_keys = [x for x in poem.keys() if "translation-" in x]
        for t_key in t_keys:
            if poem[t_key]["translator_level"] == "professional":
                for stanza in poem[t_key]["poem"].split("\n\n"):
                    data_new.append((stanza, "orig"))
                    data_new.append((stanza.replace("\n", " "), "line"))
                    data_new.append((paraphrase(stanza), "orig_parap"))
                    data_new.append((paraphrase(stanza.replace("\n", " ")), "line_parap"))
            time.sleep(1)
    print("acquired", len(data_new), "poem stanzas")

    with open(args.out, "wb") as f:
        pickle.dump(data_new, f)
