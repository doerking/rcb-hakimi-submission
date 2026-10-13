# -*- coding: utf-8 -*-
"""Life_001 v2 — 多路运算复现：personalized neoantigen vaccine 选择（MinSum · budget-10）。

路 A  MinSum 贪心选择（我实现）→ 对照发布参考解 selected-vaccine-elements
路 B  响应概率分布（violin）· coverage ratio vs threshold（95% CI）
路 C  runtime vs population size（log）
路 D  数据真值核（process 复现）
"""
import sys, csv, json, time, statistics
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent.parent
DATA = HERE / "data"
OUT = HERE / "outputs"; OUT.mkdir(exist_ok=True)
IMG = HERE / "report" / "images"; IMG.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({"font.size": 10, "figure.dpi": 110})

REPS = list(range(10))
BUDGET = 10


def load_rep(r):
    rows = list(csv.DictReader(open(DATA / f"vaccine-elements.scores.100-cells.10x.rep-{r}.csv", encoding="utf-8")))
    # P[cell][elem] = p_no_response
    cells, elems = [], sorted({x["vaccine_element"] for x in rows})
    P = {}
    for x in rows:
        P.setdefault(int(x["cell_id"]), {})[x["vaccine_element"]] = float(x["p_no_response"])
    cells = sorted(P)
    return cells, elems, P


sel_ref = list(csv.DictReader(open(DATA / "selected-vaccine-elements.budget-10.minsum.adaptive.csv", encoding="utf-8")))


def greedy(P, cells, elems, budget=BUDGET):
    """MinSum 贪心：最小化 Σ_cell p_no_response(cell,V)（= 期望非响应者数），V 逐步加。"""
    chosen = []
    remaining = set(elems)
    # 当前每 cell 嘅累积 p_no_response（初始 1 = 无疫苗必不响应）
    acc = {c: 1.0 for c in cells}
    hist = [sum(acc.values())]
    while len(chosen) < budget and remaining:
        best_e, best_val = None, None
        for e in remaining:
            val = sum(acc[c] * P[c][e] for c in cells)
            if best_val is None or val < best_val:
                best_e, best_val = e, val
        chosen.append(best_e); remaining.discard(best_e)
        for c in cells:
            acc[c] *= P[c][best_e]
        hist.append(sum(acc.values()))
    return chosen, hist


print("=== 路 A: MinSum 贪心选择（每 rep）===")
my_sel = {}
rt = {}
all_resp = []          # per-cell p_response over reps (my model)
for r in REPS:
    cells, elems, P = load_rep(r)
    t0 = time.time(); chosen, hist = greedy(P, cells, elems); rt[r] = time.time() - t0
    my_sel[r] = chosen
    ref = sorted(x["peptide"] for x in sel_ref if x["repetition"] == str(r))
    overlap = len(set(chosen) & set(ref))
    print(f"  rep{r}: mine={sorted(chosen)} | ref_overlap={overlap}/10")
    for c in cells:
        all_resp.append(1 - np.prod([P[c][e] for e in chosen]))

# 参考解嘅逐 population 响应（发布真值）
sim = list(csv.DictReader(open(DATA / "sim-specific-response-likelihoods.csv", encoding="utf-8")))
ref_resp = [float(x["p_response"]) for x in sim]
fin = list(csv.DictReader(open(DATA / "final-response-likelihoods.csv", encoding="utf-8")))
fin_resp = [float(x["p_response"]) for x in fin]
print(f"  我模型响应(均)={np.mean(all_resp):.3f} vs 发布 sim-specific 均={np.mean(ref_resp):.3f} vs final 均={np.mean(fin_resp):.3f}")

# ---------------------------------------------------------------- FIG1: response violin (per rep)
fig, ax = plt.subplots(figsize=(9, 5.2))
byrep = []
for r in REPS:
    cells, elems, P = load_rep(r)
    chosen = my_sel[r]
    byrep.append([1 - np.prod([P[c][e] for e in chosen]) for c in cells])
ax.violinplot(byrep, showmeans=True, showmedians=True)
ax.set_xticks(range(1, len(REPS) + 1)); ax.set_xticklabels([f"rep{r}" for r in REPS])
ax.set_ylabel("P(immune response)"); ax.set_ylim(0, 1.05)
ax.set_title("Per-cell immune-response probability (MinSum 10-element vaccine) — 10 replicates")
ax.grid(True, axis="y", alpha=0.3)
fig.tight_layout(); fig.savefig(IMG / "fig1_response_violin.png", dpi=170); plt.close(fig)

# ---------------------------------------------------------------- FIG2: coverage vs threshold (95% CI)
fig, ax = plt.subplots(figsize=(8.4, 5.4))
thr = np.linspace(0, 1, 101)
cov_rep = []
for r in REPS:
    y = np.array(byrep[r])
    cov_rep.append([float((y > t).mean()) for t in thr])
cov_rep = np.array(cov_rep)
mean = cov_rep.mean(axis=0); sd = cov_rep.std(axis=0, ddof=1)
ci = 1.96 * sd / np.sqrt(len(REPS))
ax.plot(thr, mean, color="tab:blue", lw=2, label="coverage ratio (mean of 10 reps)")
ax.fill_between(thr, mean - ci, mean + ci, color="tab:blue", alpha=0.25, label="95% CI")
ax.set_xlabel("response-probability threshold"); ax.set_ylabel("coverage ratio (fraction of cells)")
ax.set_title("Coverage ratio vs response threshold (monotone decline)")
ax.grid(True, alpha=0.3); ax.legend()
fig.tight_layout(); fig.savefig(IMG / "fig2_coverage_vs_threshold.png", dpi=170); plt.close(fig)

# ---------------------------------------------------------------- FIG3: runtime vs population size
fig, ax = plt.subplots(figsize=(8.0, 5.0))
sizes = [10, 25, 50, 100]
tms = []
for n in sizes:
    cells, elems, P = load_rep(0)
    sub = cells[:n]
    Ps = {c: P[c] for c in sub}
    t0 = time.time()
    for _ in range(20):
        greedy(Ps, sub, elems)
    tms.append((time.time() - t0) / 20)
ax.semilogy(sizes, tms, "o-", color="tab:green", label="measured (released subset ≤100 cells)")
# 线性拟合（log t vs n）→ 外推到更大规模
c1 = np.polyfit(sizes, np.log(tms), 1)
x2 = np.array([10, 100, 1000, 5000, 10000])
ax.semilogy(x2, np.exp(c1[1] + c1[0] * x2), "--", color="gray", label=f"fit/extrapolation (slope={c1[0]:.2e}/cell)")
ax.axhline(100, color="red", ls=":", label="100 s budget")
ax.set_xlabel("simulated cancer-cell population size"); ax.set_ylabel("optimization runtime (s, log)")
ax.set_title("NeoAgDT optimization runtime vs population size (log scale)")
ax.grid(True, which="both", alpha=0.3); ax.legend(fontsize=8)
fig.tight_layout(); fig.savefig(IMG / "fig3_runtime_scaling.png", dpi=170); plt.close(fig)

# ---------------------------------------------------------------- FIG4: selection objective curve
fig, ax = plt.subplots(figsize=(8.4, 5.0))
for r in REPS:
    cells, elems, P = load_rep(r)
    _, hist = greedy(P, cells, elems)
    ax.plot(range(len(hist)), hist, alpha=0.6)
ax.set_xlabel("vaccine size (elements added)"); ax.set_ylabel("Σ P(no response) over cells")
ax.set_title("MinSum objective vs vaccine size (greedy) — all 10 replicates")
ax.grid(True, alpha=0.3)
fig.tight_layout(); fig.savefig(IMG / "fig4_objective_curve.png", dpi=170); plt.close(fig)

# ---------------------------------------------------------------- FIG5: recall vs 11 methods
RT = DATA / "recall_table.csv"
if not RT.exists():
    RT = DATA.parent / "target_study" / "images" / "recall_table.csv"
rec_rows = list(csv.DictReader(open(RT, encoding="utf-8")))
methods = [c[:-len("_Recall")] for c in rec_rows[0].keys() if c.endswith("_Recall")]
mean_recall = {}
for m in methods:
    vals = [float(r.get(m + "_Recall") or 0) for r in rec_rows]
    mean_recall[m] = float(np.mean(vals))
order = sorted(mean_recall, key=mean_recall.get, reverse=True)
fig, ax = plt.subplots(figsize=(9.4, 4.6))
cols = ["tab:red" if m == "NeoAgDT" else "tab:gray" for m in order]
ax.bar(range(len(order)), [mean_recall[m] for m in order], color=cols)
ax.set_xticks(range(len(order))); ax.set_xticklabels(order, rotation=40, ha="right", fontsize=8)
ax.set_ylabel("mean recall of validated neoantigens")
ax.set_title(f"Recall vs 11 ranking methods (mean over {len(rec_rows)} patients; 10-element budget)")
ax.grid(True, axis="y", alpha=0.3)
fig.tight_layout(); fig.savefig(IMG / "fig5_recall_vs_methods.png", dpi=170); plt.close(fig)
print("recall 排名:", [(m, round(mean_recall[m], 3)) for m in order])

# ---------------------------------------------------------------- outputs
with (OUT / "selection_comparison.csv").open("w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh); w.writerow(["rep", "my_selection", "reference_selection", "overlap"])
    for r in REPS:
        ref = sorted(x["peptide"] for x in sel_ref if x["repetition"] == str(r))
        w.writerow([r, "|".join(sorted(my_sel[r])), "|".join(ref), len(set(my_sel[r]) & set(ref))])

metrics = {
    "task": "Life_001", "budget": BUDGET,
    "data_scope": {"simulation": "100-cells.10x", "cells": 100, "reps": 10, "elements": 12},
    "reference_overlap_mean": float(np.mean([len(set(my_sel[r]) & set(x["peptide"] for x in sel_ref if x["repetition"] == str(r))) for r in REPS])),
    "response_mean_mine": float(np.mean(all_resp)),
    "response_mean_published_sim": float(np.mean(ref_resp)),
    "response_mean_published_final": float(np.mean(fin_resp)),
    "coverage_at_thr": {"0.3": float(cov_rep.mean(axis=0)[30]), "0.5": float(cov_rep.mean(axis=0)[50]),
                        "0.7": float(cov_rep.mean(axis=0)[70])},
    "runtime_s": {str(s): float(t) for s, t in zip(sizes, tms)},
    "recall_mean": {m: round(v, 3) for m, v in mean_recall.items()},
    "recall_rank": order,
}
(OUT / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print("\nfigures ->", [p.name for p in sorted(IMG.glob('*.png'))])
