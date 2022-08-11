#!/usr/bin/env python3

import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np

# run generate_sim.py to get these results
RESULTS_CONTRAST = {
    ('orig', 'orig'): 1.0, ('orig', 'line'): 0.99920243, ('orig', 'orig_parap'): 0.99702346, ('orig', 'line_parap'): 0.99496335, ('line', 'orig'): 0.99920243, ('line', 'line'): 1.0, ('line', 'orig_parap'): 0.9964274, ('line', 'line_parap'): 0.99487275, ('orig_parap', 'orig'): 0.99702346, ('orig_parap', 'line'): 0.9964274, ('orig_parap', 'orig_parap'): 1.0, ('orig_parap', 'line_parap'): 0.99702305, ('line_parap', 'orig'): 0.99496335, ('line_parap', 'line'): 0.99487275, ('line_parap', 'orig_parap'): 0.99702305, ('line_parap', 'line_parap'): 1.0
}
RESULTS_ALL_ALL ={
    ('orig', 'orig'): 0.98882705, ('orig', 'line'): 0.9881173, ('orig', 'orig_parap'): 0.98979163, ('orig', 'line_parap'): 0.989912, ('line', 'orig'): 0.9881173, ('line', 'line'): 0.98768073, ('line', 'orig_parap'): 0.98906934, ('line', 'line_parap'): 0.9894115, ('orig_parap', 'orig'): 0.9897916, ('orig_parap', 'line'): 0.9890694, ('orig_parap', 'orig_parap'): 0.9912494, ('orig_parap', 'line_parap'): 0.9914159, ('line_parap', 'orig'): 0.9899121, ('line_parap', 'line'): 0.9894114, ('line_parap', 'orig_parap'): 0.991416, ('line_parap', 'line_parap'): 0.9921137, ('orig', 'prose'): 0.9890132, ('line', 'prose'): 0.9886554, ('orig_parap', 'prose'): 0.99018437, ('line_parap', 'prose'): 0.9912292
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

CATEGORIES = ["orig", "line", "orig_parap", "line_parap", "prose"]

if __name__ == "__main__":
    MIN_COL = min(min(RESULTS_CONTRAST.values()), min(RESULTS_ALL_ALL.values()))
    MAX_COL = max(max(RESULTS_CONTRAST.values()), max(RESULTS_ALL_ALL.values()))

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

            if CATEGORIES[j] != "prose":
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

            if CATEGORIES[j] != "prose":
                result = get_result(CATEGORIES[i], CATEGORIES[j], RESULTS_CONTRAST) 
                plt.text(
                    i+0.2, j - 1+0.25, f"{result:.3f}".lstrip("0"),
                    ha="center", va="center", color=get_color(result),
                )

    # I have no idea why this works even when we draw this the last -zouharvi
    plt.imshow(img, cmap=cmap, aspect="auto", vmin=MIN_COL, vmax=MAX_COL)

    # add "legend"
    triangle = plt.Polygon(
        np.array([[1.9, -0.3], [3.3, -0.3], [1.9, 1.1]]),
        edgecolor="black",
        facecolor="none"
    )
    ax.add_patch(triangle)
    triangle = plt.Polygon(
        np.array([[3.3, -0.3], [3.3, 1.1], [1.9, 1.1]]),
        edgecolor="black",
        facecolor="none"
    )
    ax.add_patch(triangle)
    plt.text(
        2, 0, "All pairs",
        ha="left", va="center", color="black",
    )
    plt.text(
        3.25, 0.91, "Contrastive",
        ha="right", va="center", color="black",
    )

    plt.colorbar(cmap=cmap)
    plt.tight_layout(pad=0)
    plt.savefig("figures/sim_poetry_prose.pdf")
    plt.show()
