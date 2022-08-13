#!/usr/bin/env python3

import argparse
from collections import defaultdict
import tqdm
import pickle
import numpy as np
import scipy.stats as st
import matplotlib.pyplot as plt
import sys
sys.path.append("src")
from metric.wordnet_utils import abstratness_poem
import fig_utils
from utils_local import *

if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument(
        "-i", "--input", default="computed/dataset_class_prose.pkl",
        help="Path to input dataset file"
    )
    args = args.parse_args()

    with open(args.input, "rb") as f:
        data = pickle.load(f)

    abstractness = defaultdict(list)
    for x, y in tqdm.tqdm(data):
        val = abstratness_poem(x)
        if val is not None:
            abstractness[y].append(val)

    for cat in CATEGORIES:
        vals = abstractness[cat]
        abs_int = st.t.interval(
            confidence=0.90, df=len(vals) - 1,
            loc=np.mean(vals),
            scale=st.sem(vals)
        )
        print(
            f"{cat:>10}:",
            f"{np.average(vals):.2f} ({abs_int[0]:.2f}, {abs_int[1]:.2f})"
        )

    plt.figure(figsize=(5, 2.5))
    violin_parts = plt.violinplot(
        list(abstractness.values()),
        showmeans=True,
        showextrema=False,
        widths=0.7,
    )

    for pc in violin_parts['bodies']:
        pc.set_facecolor(fig_utils.COLORS_FIRE[0])
        pc.set_edgecolor('black')
        pc.set_linewidth(1.2)
        pc.set_alpha(0.75)
        pc.set_aa(True)
    violin_parts['cmeans'].set_linewidth(1.2)
    violin_parts['cmeans'].set_color("black")

    for cat_i, cat in enumerate(CATEGORIES):
        plt.text(
            cat_i+0.5, 0.325,
            f"{np.average(abstractness[cat]):.2f}",
            fontsize=9,
        )

    plt.ylim(0.3, 1)
    plt.xticks(
        range(1, len(abstractness)+1),
        [PRETTY_NAMES[x] for x in abstractness.keys()],
        fontsize=9,
    )
    plt.ylabel("Abstractness")
    plt.tight_layout(pad=0)
    plt.savefig("figures/abstractness_poetry_prose.pdf")
    plt.show()