"""vizstyle.py -- one shared look for every figure in this solution.

The palette is the validated categorical set described in the repo's
data-visualisation guidance, used **in slot order and never cycled**:

    slot 1 blue    #2a78d6      slot 5 magenta #e87ba4
    slot 2 orange  #eb6834      slot 6 green   #008300
    slot 3 aqua    #1baf7a      slot 7 violet  #4a3aa7
    slot 4 yellow  #eda100      slot 8 red     #e34948

Checked with the palette validator for the subsets actually used here
(2, 3, 4 and 5 adjacent slots, light surface): lightness band, chroma floor,
colour-vision-deficiency separation and normal-vision separation all pass.
Three slots sit below 3:1 contrast on a white surface, so the "relief rule"
applies -- every figure here ships next to a CSV and a markdown table, and
series are direct-labelled or legended, so identity is never colour-alone.
"""

from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
INK_MUTED = "#8a8880"

SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100",
          "#e87ba4", "#008300", "#4a3aa7", "#e34948"]

GOOD = "#1baf7a"
BAD = "#e34948"


def use_style() -> None:
    plt.rcParams.update({
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "savefig.facecolor": SURFACE,
        "axes.edgecolor": INK_MUTED,
        "axes.labelcolor": INK_2,
        "axes.titlecolor": INK,
        "axes.titlesize": 12,
        "axes.titleweight": "normal",
        "axes.labelsize": 10,
        "axes.grid": True,
        "axes.axisbelow": True,
        "grid.color": "#d9d8d2",
        "grid.linewidth": 0.6,
        "grid.alpha": 0.7,
        "xtick.color": INK_2,
        "ytick.color": INK_2,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "legend.frameon": False,
        "legend.fontsize": 9,
        "legend.labelcolor": INK_2,
        "lines.linewidth": 1.6,
        "lines.markersize": 5,
        "font.size": 10,
        "figure.dpi": 150,
    })


def despine(ax) -> None:
    """Recessive frame: keep the two axes that carry the scale, drop the rest."""
    ax.spines[["top", "right"]].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(INK_MUTED)
        ax.spines[s].set_linewidth(0.8)
