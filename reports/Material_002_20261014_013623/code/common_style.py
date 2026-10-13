"""Common matplotlib style for reproducing the MACE-MP-0 target figures.

- Enables Chinese font (Microsoft YaHei) so labels match the target figures.
- Returns a fresh figure/axes with the same visual recipe used across the
  three reproduction plots.
"""
from __future__ import annotations

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib import rcParams

# --- Chinese-friendly font setup (matches target's Chinese labels) ----------
rcParams["font.sans-serif"] = [
    "Microsoft YaHei",
    "Microsoft JhengHei",
    "SimHei",
    "Noto Sans CJK SC",
    "DejaVu Sans",
]
rcParams["axes.unicode_minus"] = False
rcParams["font.size"] = 11
rcParams["axes.titlesize"] = 12
rcParams["axes.grid"] = True
rcParams["grid.color"] = "#cccccc"
rcParams["grid.linewidth"] = 0.6
rcParams["grid.alpha"] = 0.7
rcParams["figure.dpi"] = 130
rcParams["savefig.dpi"] = 150
rcParams["savefig.bbox"] = "tight"
rcParams["lines.linewidth"] = 1.6
rcParams["xtick.direction"] = "out"
rcParams["ytick.direction"] = "out"


def new_fig(size=(8.0, 6.0)):
    """Return a fresh Figure, Axes pair with the shared style."""
    fig, ax = plt.subplots(figsize=size)
    ax.set_facecolor("white")
    fig.patch.set_facecolor("white")
    return fig, ax
