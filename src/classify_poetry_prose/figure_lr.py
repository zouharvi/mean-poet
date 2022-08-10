#!/usr/bin/env python3

import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np

# run run_classifier.py to get these results
RESULTS = {
    ('orig', 'line'): 0.7767857142857143, ('orig', 'orig_parap'): 0.5535714285714286, ('orig', 'line_parap'): 0.8839285714285714, ('orig', 'prose'): 0.9821428571428571, ('line', 'orig_parap'): 0.8928571428571429,
    ('line', 'line_parap'): 0.5357142857142857, ('line', 'prose'): 0.9375, ('orig_parap', 'line_parap'): 0.7946428571428571, ('orig_parap', 'prose'): 0.9642857142857143, ('line_parap', 'prose'): 0.9107142857142857
}

PRETTY_NAMES = {
    "orig": "Original",
    "line": "No newlines",
    "orig_parap": "Original\ndepoeticised",
    "line_parap": "No newlines\ndepoeticised",
    "prose": "Prose",
}
PRETTY_NAMES_2 = PRETTY_NAMES | {
    "orig_parap": "Original\ndepoet.",
    "line_parap": "No newlines\ndepoet.",
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
    CATEGORIES = ["orig", "line", "orig_parap", "line_parap", "prose"]
    CATEGORIES_PRETTY = [PRETTY_NAMES[x] for x in CATEGORIES]
    CATEGORIES_PRETTY_2 = [PRETTY_NAMES_2[x] for x in CATEGORIES]
    no_classes = len(CATEGORIES)
    img = np.full((no_classes - 1, no_classes - 1), fill_value=np.nan)

    plt.figure(figsize=(5, 2.5))
    plt.yticks(range(no_classes - 1), CATEGORIES_PRETTY[1:])
    plt.xticks(range(no_classes - 1), CATEGORIES_PRETTY_2[:-1])

    ax = plt.gca()
    ax.tick_params(axis="x", bottom=False)
    ax.tick_params(axis="y", left=False)

    cmap = mpl.cm.get_cmap("inferno").copy()
    cmap.set_bad('gray',0.2)

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
    plt.colorbar()
    plt.tight_layout(pad=0)
    plt.savefig("figures/classify_poetry_prose.pdf")
    plt.show()
