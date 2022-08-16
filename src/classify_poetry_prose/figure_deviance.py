#!/usr/bin/env python3

import argparse
import pickle
import sys
sys.path.append("src")
import matplotlib.pyplot as plt
import fig_utils
import numpy as np
from nltk import word_tokenize, pos_tag
from utils_local import *
from metric.wordnet_utils import meaning_overlap, meaning_overlap_lexical


def get_color(val):
    if val > 0.25:
        return "black"
    else:
        return "white"


if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument(
        # output of classify_poetry_prose/translate_deviance
        "-d", "--dataset", default="computed/dataset_class_deviance.pkl",
        help="Path to embedding file"
    )
    args = args.parse_args()
    with open(args.dataset, "rb") as f:
        data = pickle.load(f)

    y_lexical = [
        (meaning_overlap_lexical(sent_src, sent_tgt), domain)
        for sent_src, sent_tgt, domain in data
    ]
    y_meaning = [
        (meaning_overlap(sent_src, sent_tgt), domain)
        for sent_src, sent_tgt, domain in data
    ]
    y_meaning_hh = [
        (meaning_overlap(sent_src, sent_tgt, hypo_hype=True), domain)
        for sent_src, sent_tgt, domain in data
    ]

    fig = plt.figure(figsize=(3.8, 2))
    ax = fig.gca()
    ax.tick_params(axis="x", bottom=False)
    ax.tick_params(axis="y", left=False)

    img = np.zeros((3, 3))

    for y_i, ys in enumerate([y_lexical, y_meaning, y_meaning_hh]):
        for d_i, domain in enumerate(["poetry", "books", "news"]):
            val = np.average([s for s, d_val in ys if d_val == domain])
            img[d_i, y_i] = val
            plt.text(
                y_i, d_i, f"{val:.2f}",
                ha="center", va="center",
                color=get_color(val)
            )

    plt.yticks([0, 1, 2], ["Poetry", "Books", "News"])
    plt.xticks([0, 1, 2], ["Lexical", "Synonym", "Synonym+\nHypo.+Hype."])
    ax.get_xaxis().set_ticks_position("top")

    plt.imshow(img, aspect="auto", cmap="inferno")
    plt.colorbar(pad=0.02)
    plt.tight_layout(rect=[-0.03, -0.03, 1.03, 1.02])
    plt.savefig("figures/deviance_poetry_prose.pdf")
    plt.show()
