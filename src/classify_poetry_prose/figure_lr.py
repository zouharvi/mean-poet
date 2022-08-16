#!/usr/bin/env python3

import sys
sys.path.append("src")
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import fig_utils
from utils_local import *

# run run_classifier.py to get these results
RESULTS = {
    ('orig', 'line'): 0.7767857142857143, ('orig', 'orig_parap'): 0.5535714285714286, ('orig', 'line_parap'): 0.8839285714285714, ('orig', 'books'): 0.9821428571428571, ('orig', 'news'): 1.0, ('line', 'orig_parap'): 0.8928571428571429, ('line', 'line_parap'): 0.5178571428571429, ('line', 'books'): 0.9375, ('line', 'news'): 1.0, ('orig_parap', 'line_parap'): 0.7767857142857143, ('orig_parap', 'books'): 0.9642857142857143, ('orig_parap', 'news'): 1.0, ('line_parap', 'books'): 0.8928571428571429, ('line_parap', 'news'): 1.0, ('books', 'news'): 1.0
}

def get_result(cat1, cat2):
    if (cat1, cat2) in RESULTS:
        return RESULTS[(cat1, cat2)]
    else:
        return RESULTS[(cat2, cat1)]


def get_color(val):
    if val > 0.6:
        return "black"
    else:
        return "white"


if __name__ == "__main__":
    CATEGORIES_PRETTY = [PRETTY_NAMES[x] for x in CATEGORIES]
    no_classes = len(CATEGORIES)
    img = np.full((no_classes - 1, no_classes - 1), fill_value=np.nan)

    plt.figure(figsize=(5, 2.5))
    plt.yticks(range(no_classes - 1), CATEGORIES_PRETTY[1:], fontsize=9)
    plt.xticks(range(no_classes - 1), CATEGORIES_PRETTY[:-1], fontsize=8)

    ax = plt.gca()
    ax.tick_params(axis="x", bottom=False)
    ax.tick_params(axis="y", left=False)

    cmap = mpl.cm.get_cmap("inferno").copy()
    cmap.set_bad('gray', 0.2)

    for i in range(len(CATEGORIES)):
        for j in range(len(CATEGORIES)):
            if i >= j:
                continue
            result = get_result(CATEGORIES[i], CATEGORIES[j])
            img[j - 1, i] = result
            plt.text(
                i, j - 1, f"{result:.1%}",
                ha="center", va="center", color=get_color(result)
            )

    plt.imshow(img, cmap=cmap, aspect="auto", vmin=0.5, vmax=1)
    plt.colorbar(pad=0.01)
    plt.tight_layout(pad=0)
    plt.savefig("figures/classify_poetry_prose.pdf")
    plt.show()
 