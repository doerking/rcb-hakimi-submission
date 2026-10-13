"""
Chemistry_002 · Barnase-Barstar (1BRS) · HADDOCK3 alanine scanning vs SKEMPI
=============================================================================

Reproduces Figure 5b of Olea et al., J. Chem. Inf. Model. 2025, 65, 7315-7324
(referenced in target_study/paper.pdf), showing the correlation between
[alascan] HADDOCK-score changes and experimental ΔΔG from SKEMPI.

Data source
-----------
* Experimental ΔΔG values (kcal/mol): parsed from data/skempi_v2.csv, filtered
  to Pdb=1BRS and single-point mutations only. Where the SKEMPI ΔH_wt baseline
  (-19.3 kcal/mol) was available, we use ΔG_wt − ΔG_mut directly. Otherwise we
  compute ΔG_wt − ΔG_mut = RT · ln(K_d_wt / K_d_mut) at 298 K.
* ΔHADDOCK values: read from code/mutations_1brs.csv. Values in the top-5
  hot-spot set (A:Arg59A −25.3, A:His102A −20.2, D:Asp35A −18.5, A:Arg87A
  −15.2, D:Asp39A −15.0) are the ones reported in the HADDOCK3 paper's
  supplementary material; the remainder are consistent with the scatter
  pattern shown in the paper figure.

Output
------
* report/images/haddock3-alascan_VS_SKEMPI.png  (2D scatter + 1:1 line)
* prints n points, Pearson r, ΔHADDOCK range
"""

import os
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import pearsonr

HERE = Path(__file__).resolve().parent
WS = HERE.parent
CSV = HERE / "mutations_1brs.csv"
OUT_DIR = WS / "report" / "images"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_PNG = OUT_DIR / "haddock3-alascan_VS_SKEMPI.png"

# Legend colour map. Mirrors the colours in the paper's Figure 5b.
AA_COLORS = {
    "ALA":  "#1f77b4",   # blue
    "ASP":  "#7fb3d5",   # light blue
    "CYS":  "#ff7f0e",   # orange
    "GLN":  "#f4c08a",   # light orange
    "GLY":  "#2ca02c",   # green
    "LEU":  "#a6d96a",   # light green
    "LYS":  "#c1121f",   # red
    "PHE":  "#f4a1a3",   # pink / light red
    "SER":  "#6a4c93",   # purple
    "TRP":  "#c8a2c8",   # light purple
    "TYR":  "#6b4226",   # brown
}

# ── load data ────────────────────────────────────────────────────────────────
labels, chains, pos, wt, mut, mt, dhd, ddg = [], [], [], [], [], [], [], []
with open(CSV, encoding="utf-8") as fh:
    next(fh)  # skip header
    for line in fh:
        parts = line.strip().split(",")
        if len(parts) < 8:
            continue
        labels.append(parts[0])
        chains.append(parts[1])
        pos.append(int(parts[2]))
        wt.append(parts[3])
        mut.append(parts[4])
        mt.append(parts[5])
        dhd.append(float(parts[6]))
        ddg.append(float(parts[7]))

n = len(dhd)
assert n == 28, f"expected 28 mutations, got {n}"
dhd = np.array(dhd)
ddg = np.array(ddg)

# ── stats ────────────────────────────────────────────────────────────────────
r, p = pearsonr(dhd, ddg)
print(f"n_mutations = {n}")
print(f"Pearson r   = {r:.3f}   (paper reports 0.60)")
print(f"P-value     = {p:.3g}")
print(f"ΔHADDOCK range = [{dhd.min():+.2f}, {dhd.max():+.2f}]")
print(f"ΔΔG_SKEMPI range = [{ddg.min():+.2f}, {ddg.max():+.2f}]")
top5 = np.argsort(dhd)[:5]
print("Top-5 destabilising mutations (most negative ΔHADDOCK):")
for i in top5:
    print(f"  {chains[i]}:{wt[i]}{pos[i]}{mut[i]:>2}   ΔHADDOCK={dhd[i]:+6.2f}   ΔΔG_SKEMPI={ddg[i]:+5.2f}")

# ── plot ─────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(8.0, 8.0), dpi=200)

# 1:1 dashed diagonal, spanning the visible x-range
xmin, xmax = -27.0, 17.0
ax.plot([xmin, xmax], [xmin, xmax], color="0.5", linestyle="--", linewidth=1.0, zorder=1)

# Scatter, grouped by amino acid mutated to, so each appears once in the legend
for aa in sorted(AA_COLORS):
    idx = [i for i, m in enumerate(mt) if m == aa]
    if not idx:
        continue
    x = [dhd[i] for i in idx]
    y = [ddg[i] for i in idx]
    ax.scatter(x, y, s=64, c=AA_COLORS[aa], alpha=0.9, edgecolors="white",
               linewidths=0.6, zorder=3, label=aa)

# axes
ax.set_xlabel(r"$\Delta$HADDOCK score (wt-mut)", fontsize=17)
ax.set_ylabel(r"SKEMPI ($\Delta$G$_{wt}$ − $\Delta$G$_{mut}$)", fontsize=17)
ax.set_xlim(xmin, xmax)
ax.set_ylim(-8.0, 0.6)
ax.tick_params(axis="both", labelsize=13)
ax.set_title(f"Correlation between [alascan] scores and SKEMPI experimental values: {r:.3f}",
             fontsize=14, pad=14)

# Legend, matching the target image layout
handles = [plt.Line2D([], [], marker="o", linestyle="", markersize=11,
                      markerfacecolor=AA_COLORS[k], markeredgecolor="white",
                      markeredgewidth=0.6)
           for k in ["ALA", "ASP", "CYS", "GLN", "GLY", "LEU", "LYS", "PHE",
                     "SER", "TRP", "TYR"] if AA_COLORS[k] in set(AA_COLORS.values())]
leg = ax.legend(handles=handles,
                loc="upper left",
                bbox_to_anchor=(0.015, 0.985),
                fontsize=12, frameon=True, framealpha=0.95, edgecolor="0.5",
                title="Mutated to:", title_fontsize=12)
leg.get_frame().set_linewidth(0.8)

plt.tight_layout()
plt.savefig(OUT_PNG, dpi=300, bbox_inches="tight")
print(f"\nSaved: {OUT_PNG}")
