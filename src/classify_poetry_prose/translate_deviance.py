#!/usr/bin/env python3

import time
import datasets
import tqdm
import json
import argparse
import pickle
from googletrans import Translator
translator = Translator()


def translate(stanza, src_lang, tgt_lang):
    poem_hyp = translator.translate(
        stanza, dest=tgt_lang, src=src_lang,
    ).text

    return poem_hyp


if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument(
        "-d", "--dataset", default="computed/dataset.jsonl",
        help="Path to dataset file"
    )
    args.add_argument(
        "-o", "--out", default="computed/dataset_class_deviance.pkl",
        help="Path to output dataset file"
    )
    args = args.parse_args()

    with open(args.dataset, "r") as f:
        data_poetry = [json.loads(x) for x in f.readlines()]

    data_new = []


    for poem_i, poem in enumerate(tqdm.tqdm(data_poetry)):
        t_keys = [x for x in poem.keys() if "translation-" in x]
        # when multiple translations are available, consider them all
        for t_key in t_keys:
            if poem[t_key]["translator_level"] == "professional":
                for stanza_ref, stanza_src in zip(poem[t_key]["poem"].split("\n\n"), poem["poem"].split("\n\n")):
                    data_new.append((
                        (
                            stanza_src.replace("\n", " "),
                            stanza_ref.replace("\n", " ")
                        ),
                        "poetry",
                        poem["lang"],  # source language
                    ))

    print("acquired", len(data_new), "poem stanzas")

    class_size = len(data_new)
    data_books = iter(datasets.load_dataset("opus_books", "de-en")["train"])
    data_news = iter(datasets.load_dataset("wmt19", "cs-en")["train"])
    # exhaust the news iterator a bit
    [next(data_news) for i in range(1000)]
    data_new_books = []
    data_new_news = []

    while len(data_new_books) < class_size:
        sent = next(data_books)["translation"]
        len_en = len(sent["en"].split())
        len_xx = len(sent["de"].split())
        if len_en < 15 or len_xx > 50 or abs(len_xx-len_en) > 8:
            continue 
        data_new_books.append((
            (sent["de"], sent["en"]),
            "books", "de"
        ))

    while len(data_new_news) < class_size:
        sent = next(data_news)["translation"]
        len_en = len(sent["en"].split())
        len_xx = len(sent["cs"].split())
        if len_en < 15 or len_xx > 50 or abs(len_xx-len_en) > 8:
            continue 
        data_new_news.append((
            (sent["cs"], sent["en"]),
            "news", "cs"
        ))

    data_new += data_new_books + data_new_news

    print("acquired", len(data_new), "lines in total")

    data_final = []
    for (sent_src, sent_hyp), domain, lang_src in tqdm.tqdm(data_new):
        data_final.append((translate(sent_src, lang_src, "en"), sent_hyp, domain))
        time.sleep(0.4)

    with open(args.out, "wb") as f:
        pickle.dump(data_final, f)
