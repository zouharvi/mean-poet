#!/usr/bin/env python3

import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from utils_local import *

# run generate_sim.py to get these results
RESULTS_CONTRAST = {('orig', 'orig'): 1.0, ('orig', 'line'): 0.99920243, ('orig', 'orig_parap'): 0.99702346, ('orig', 'line_parap'): 0.99496335, ('line', 'orig'): 0.99920243, ('line', 'line'): 1.0, ('line', 'orig_parap'): 0.9964274, ('line', 'line_parap'): 0.99487275, ('orig_parap', 'orig'): 0.99702346, ('orig_parap', 'line'): 0.9964274, ('orig_parap', 'orig_parap'): 1.0, ('orig_parap', 'line_parap'): 0.99702305, ('line_parap', 'orig'): 0.99496335, ('line_parap', 'line'): 0.99487275, ('line_parap', 'orig_parap'): 0.99702305, ('line_parap', 'line_parap'): 1.0}

RESULTS_ALL_ALL = {('orig', 'orig'): 0.98882705, ('orig', 'line'): 0.9881173, ('orig', 'orig_parap'): 0.98979163, ('orig', 'line_parap'): 0.989912, ('line', 'orig'): 0.9881173, ('line', 'line'): 0.98768073, ('line', 'orig_parap'): 0.98906934, ('line', 'line_parap'): 0.9894115, ('orig_parap', 'orig'): 0.9897916, ('orig_parap', 'line'): 0.9890694, ('orig_parap', 'orig_parap'): 0.9912494, ('orig_parap', 'line_parap'): 0.9914159, ('line_parap', 'orig'): 0.9899121, ('line_parap', 'line'): 0.9894114, ('line_parap', 'orig_parap'): 0.991416, ('line_parap', 'line_parap'): 0.9921137, ('orig', 'books'): 0.9890132, ('orig', 'news'): 0.9877535, ('line', 'books'): 0.9886554, ('line', 'news'): 0.9872868, ('orig_parap', 'books'): 0.99018437, ('orig_parap', 'news'): 0.9894691, ('line_parap', 'books'): 0.9912292, ('line_parap', 'news'): 0.98987967, ('news', 'books'): 0.98926544, ('books', 'news'): 0.98926544}

def get_result(cat1, cat2, results):
    if (cat1, cat2) in results:
        return results[(cat1, cat2)]
    else:
        return results[(cat2, cat1)]


def get_color(val):
    if val > 0.992:
        return "black"
    else:
        return "white"

if __name__ == "__main__":
    MIN_COL = min(min(RESULTS_CONTRAST.values()), min(RESULTS_ALL_ALL.values()))
    MAX_COL = max(max(RESULTS_CONTRAST.values()), max(RESULTS_ALL_ALL.values()))

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
    cmap.set_bad('gray',0.2)

    for i in range(len(CATEGORIES)):
        for j in range(len(CATEGORIES)):
            if i >= j:
                continue

            if CATEGORIES[j] not in {"books", "news"}:
                result = get_result(CATEGORIES[i], CATEGORIES[j], RESULTS_CONTRAST)
                img[j - 1, i] = result
            else:
                img[j-1, i] = None

            result = get_result(CATEGORIES[i], CATEGORIES[j], RESULTS_ALL_ALL)
            triangle = plt.Polygon(
                np.array([[i, j-1], [i+1, j-1], [i, j]])-0.5,
                # color input needs to be normalized
                color=cmap((result-MIN_COL)/(MAX_COL-MIN_COL))
            )
            ax.add_patch(triangle)

            plt.text(
                i-0.2, j - 1-0.25, f"{result:.3f}".lstrip("0"),
                ha="center", va="center", color=get_color(result),
            )

            if CATEGORIES[j] not in {"books", "news"}:
                result = get_result(CATEGORIES[i], CATEGORIES[j], RESULTS_CONTRAST) 
                plt.text(
                    i+0.2, j - 1+0.25, f"{result:.3f}".lstrip("0"),
                    ha="center", va="center", color=get_color(result),
                )

    # I have no idea why this works even when we draw this the last -zouharvi
    plt.imshow(img, cmap=cmap, aspect="auto", vmin=MIN_COL, vmax=MAX_COL)

    # add "legend"
    triangle = plt.Polygon(
        np.array([[2.9, -0.3], [4.3, -0.3], [2.9, 1.1]]),
        edgecolor="black",
        facecolor="none"
    )
    ax.add_patch(triangle)
    triangle = plt.Polygon(
        np.array([[4.3, -0.3], [4.3, 1.1], [2.9, 1.1]]),
        edgecolor="black",
        facecolor="none"
    )
    ax.add_patch(triangle)
    plt.text(
        3, 0, "All pairs",
        ha="left", va="center", color="black",
        fontsize=9,
    )
    plt.text(
        4.25, 0.91, "Contrastive",
        ha="right", va="center", color="black",
        fontsize=8.5,
    )

    plt.colorbar(cmap=cmap, pad=0.01)
    plt.tight_layout(pad=0)
    plt.savefig("figures/sim_poetry_prose.pdf")
    plt.show()
