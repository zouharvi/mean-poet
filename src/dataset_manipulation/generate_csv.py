#!/usr/bin/env python3

import sys
sys.path.append("src")
import json
import argparse
import csv
import random

FIELDNAMES = [
    "title",
    "t_key",
    "translator",
    "translator_level",
    "stanza_i",
    "src",
    "hyp",
]

if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument(
        "-d", "--dataset", default="computed/dataset.jsonl",
        help="Path to dataset file"
    )
    args.add_argument(
        "-o", "--out", default="computed/dataset.csv",
        help="Path to annotation dataset csv file"
    )
    args = args.parse_args()

    with open(args.dataset, "r") as f:
        data = [json.loads(x) for x in f.readlines()]

    with open(args.out, "w") as f:
        f.write(",".join(FIELDNAMES + ["Meaning", "Poeticness", "Overall"]) + "\n")
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)

        for poem in data:
            t_keys = [x for x in poem.keys() if "translation-" in x]
            poem_hyps = [
                # split to stanza
                {
                    "title": poem["title"],
                    "t_key": t_key,
                    "translator": poem[t_key]["translator"],
                    "translator_level": poem[t_key]["translator_level"],
                    "stanzas": poem[t_key]["poem"].split("\n\n"),
                }
                for t_key in t_keys
            ]
            # check that all poems have the same number of stanzas
            if not all([len(x["stanzas"]) == len(poem_hyps[0]["stanzas"]) for x in poem_hyps]):
                print(
                    poem["title"],
                    "does not have the same number of stanzas, exiting"
                )
                print([len(x) == len(poem_hyps[0]) for x in poem_hyps])
                exit()

            stanzas_src = poem["poem"].split("\n\n")

            # transpose but a bit more complicated because of the inner structure
            stanzas_hyps = [
                [
                    poem_hyps[t_key] | {"hyp": poem_hyps[t_key]["stanzas"][stanza_i]}
                    for t_key in range(len(poem_hyps))
                ]
                for stanza_i in range(len(poem_hyps[0]["stanzas"]))
            ]

            # make sure that the source and all the translations have the same number of stanzas
            assert len(stanzas_src) == len(stanzas_hyps)
            for stanza_i, (stanza_src, stanza_hyps) in enumerate(zip(stanzas_src, stanzas_hyps)):
                # delete stanzas because they do not belong there and CsvWriter complains
                for stanza_hyp in stanza_hyps:
                    del stanza_hyp["stanzas"]
                
                stanza_hyps = [
                    stanza_hyp | {"stanza_i": stanza_i, "src": stanza_src}
                    for stanza_hyp  in stanza_hyps
                ]
                random.shuffle(stanza_hyps)

                writer.writerows(stanza_hyps)

            writer.writerow({})
