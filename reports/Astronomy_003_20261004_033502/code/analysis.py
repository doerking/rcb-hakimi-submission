#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Astronomy_003 — BBH numerical-relativity waveform convergence analysis (re-discovery).

Blind protocol: target_study/ 全程未讀。只用 data/ 三個 fig_data。

Data -> paper figure mapping (from task_info descriptions, not from target_study):
  fig6_data.csv : waveform difference between the two highest numerical resolutions
  fig7_data.csv : same differences decomposed by spherical-harmonic mode l=2..8
  fig8_data.csv : extrapolation-order contrasts (N=2 vs N=3, N=2 vs N=4)
"""
from __future__ import annotations
import csv, json, math, statistics as st
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

WS = Path(__file__).resolve().parent.parent
DATA, IMG, OUT = WS / "data", WS / "report" / "images", WS / "outputs"
IMG.mkdir(parents=True, exist_ok=True)

def col(f, c):
    with open(DATA / f, newline="", encoding="utf-8") as fh:
        return np.array([float(r[c]) for r in csv.DictReader(fh) if r[c].strip()])

d6 = col("fig6_data.csv", "waveform_difference")
ells = {f"ell{k}": col("fig7_data.csv", f"ell{k}") for k in range(2, 9)}
n3, n4 = col("fig8_data.csv", "N2vsN3"), col("fig8_data.csv", "N2vsN4")

M = {}
plt.rcParams.update({"figure.dpi": 150, "font.size": 9, "axes.grid": True, "grid.alpha": .3})

# ── core statistics ─────────────────────────────────────────────────────
def s(x):
    x = np.asarray(x, float)
    return {"n": int(len(x)), "min": float(x.min()), "median": float(np.median(x)),
            "mean": float(x.mean()), "max": float(x.max()),
            "log10_mean": float(np.mean(np.log10(x))), "log10_std": float(np.std(np.log10(x)))}
M["fig6"] = s(d6)
M["fig7"] = {k: s(v) for k, v in ells.items()}
M["fig8"] = {"N2vsN3": s(n3), "N2vsN4": s(n4)}

# ── ratio tests ─────────────────────────────────────────────────────────
M["fig8_ratio"] = {"median(N4/N3)": float(np.median(n4 / n3)), "mean(N4/N3)": float(np.mean(n4 / n3)),
                   "frac_N4_gt_N3": float(np.mean(n4 > n3))}
# mode trend: median vs l
ls = np.array([int(k[3:]) for k in ells])
med = np.array([np.median(v) for v in ells.values()])
slope = float(np.polyfit(np.log10(ls), np.log10(med), 1)[0])
M["mode_trend"] = {"median_by_l": {k: float(np.median(v)) for k, v in ells.items()},
                   "power_law_slope_vs_l": slope,
                   "median_ratio_l8_over_l2": float(np.median(ells["ell8"]) / np.median(ells["ell2"]))}
# consistency: sum over modes vs total difference?
tot_modes = np.sum(list(ells.values()), axis=0)
M["consistency"] = {"corr_sum_modes_vs_fig6": float(np.corrcoef(tot_modes[:len(d6)], np.log10(d6))[0, 1]),
                    "median_ratio_sum_over_fig6": float(np.median(tot_modes[:len(d6)] / d6))}

json.dump(M, open(OUT / "metrics.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ══ F1 · fig6 distribution ══════════════════════════════════════════════
fig, ax = plt.subplots(1, 2, figsize=(9, 3.2))
ax[0].hist(np.log10(d6), bins=50, color="#4C78A8"); ax[0].set_xlabel("log10 waveform difference"); ax[0].set_title("Fig6 — distribution")
xs = np.sort(d6); ccdf = 1 - np.arange(1, len(xs) + 1) / len(xs)
ax[1].loglog(xs, ccdf, color="#D62728"); ax[1].set_xlabel("waveform difference"); ax[1].set_ylabel("P(X > x)")
ax[1].set_title("Fig6 — CCDF")
fig.tight_layout(); fig.savefig(IMG / "fig1_fig6_distribution.png"); plt.close(fig)

# ══ F2 · fig7 mode decomposition ════════════════════════════════════════
fig, ax = plt.subplots(1, 2, figsize=(9.4, 3.4))
ax[0].boxplot([ells[k] for k in ells], tick_labels=[k[3:] for k in ells], showfliers=False)
ax[0].set_yscale("log"); ax[0].set_xlabel("spherical-harmonic mode $\\ell$"); ax[0].set_ylabel("waveform difference")
ax[0].set_title("Fig7 — error by mode")
ax[1].loglog(ls, med, "o-", color="#4C78A8", label=f"median (slope {slope:.2f})")
ax[1].loglog(ls, [np.mean(v) for v in ells.values()], "s--", color="#F58518", label="mean")
ax[1].set_xlabel("$\\ell$"); ax[1].set_ylabel("difference"); ax[1].set_title("Fig7 — mode trend"); ax[1].legend()
fig.tight_layout(); fig.savefig(IMG / "fig2_fig7_modes.png"); plt.close(fig)

# ══ F3 · fig8 extrapolation order ══════════════════════════════════════
fig, ax = plt.subplots(1, 3, figsize=(11, 3.2))
ax[0].hist(np.log10(n3), bins=45, alpha=.65, label="N2vsN3", color="#4C78A8")
ax[0].hist(np.log10(n4), bins=45, alpha=.65, label="N2vsN4", color="#D62728")
ax[0].set_xlabel("log10 difference"); ax[0].set_title("Fig8 — distributions"); ax[0].legend()
ax[1].boxplot([n3, n4], tick_labels=["N2vsN3", "N2vsN4"], showfliers=False); ax[1].set_yscale("log")
ax[1].set_title("Fig8 — order contrast")
r = n4 / n3
ax[2].hist(np.log10(r), bins=45, color="#54A24B")
ax[2].axvline(0, color="k", ls="--", lw=1.2)
ax[2].set_xlabel("log10(N2vsN4 / N2vsN3)"); ax[2].set_title(f"Ratio (N4/N3): median {np.median(r):.2f}×")
fig.tight_layout(); fig.savefig(IMG / "fig3_fig8_orders.png"); plt.close(fig)

# ══ F4 · consistency check ═════════════════════════════════════════════
fig, ax = plt.subplots(1, 2, figsize=(9, 3.2))
n = min(len(d6), tot_modes.shape[0])
ax[0].loglog(d6[:n], tot_modes[:n], ".", ms=2, alpha=.3, color="#4C78A8")
ax[0].set_xlabel("fig6 total difference"); ax[0].set_ylabel("sum over modes (fig7)")
ax[0].set_title("Consistency: fig6 vs sum of modes")
ax[1].boxplot([np.log10(d6), np.log10(tot_modes[:n])], tick_labels=["fig6 total", "sum modes"],
              showfliers=False)
ax[1].set_ylabel("log10 difference"); ax[1].set_title("Total vs mode-sum")
fig.tight_layout(); fig.savefig(IMG / "fig4_consistency.png"); plt.close(fig)

# ══ F5 · joint view ════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(6.6, 3.4))
data = [np.log10(d6)] + [np.log10(ells[k]) for k in ells] + [np.log10(n3), np.log10(n4)]
lbl = ["fig6"] + [k[3:] for k in ells] + ["N2vsN3", "N2vsN4"]
bp = ax.boxplot(data, tick_labels=lbl, showfliers=False, patch_artist=True)
for i, b in enumerate(bp["boxes"]):
    b.set_facecolor("#D62728" if i == 0 else ("#F58518" if i <= 7 else "#4C78A8"))
ax.set_ylabel("log10 waveform difference"); ax.set_title("All released quantities (log scale)")
fig.tight_layout(); fig.savefig(IMG / "fig5_all_quantities.png"); plt.close(fig)

print(json.dumps(M, ensure_ascii=False, indent=1)[:1600])
print("figures:", sorted(p.name for p in IMG.glob("*.png")))
