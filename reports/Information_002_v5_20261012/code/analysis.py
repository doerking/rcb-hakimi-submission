# -*- coding: utf-8 -*-
"""Information_002 — Reproduction: structured extraction + step scoring of a multi-step
Hartree-Fock derivation pipeline (paper 2111.01152, AB-stacked MoTe2/WSe2 moire).

Deliverable: a machine-readable extraction of the paper's step decomposition (task / source lines /
placeholders / reference answer), together with an automated step-scoring summary and a
placeholder-level comparison of LLM vs human answers with inter-annotator agreement.
"""
import re, json, csv, statistics
from pathlib import Path

import numpy as np
import yaml
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent.parent
DATA = HERE / "data" / "2111.01152"
OUT = HERE / "outputs"; OUT.mkdir(exist_ok=True)
IMG = HERE / "report" / "images"; IMG.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({"font.size": 10, "figure.dpi": 110})

raw = yaml.safe_load((DATA / "2111.01152.yaml").read_text(encoding="utf-8"))
meta = raw[0]
DIMS = ["in_paper", "prompt_quality", "follow_instructions", "physics_logic",
        "math_derivation", "final_answer_accuracy"]
steps = []
for i, it in enumerate(raw[1:], 1):
    if not isinstance(it, dict) or not it.get("task"):
        continue
    ph = it.get("placeholder") or {}
    ph_rows = []
    for name, spec in ph.items():
        spec = spec or {}
        sc = spec.get("score") or {}
        vals = [v for v in sc.values() if isinstance(v, (int, float))]
        llm, hum = spec.get("LLM"), spec.get("human")
        same = None
        if llm is not None and hum is not None:
            n = lambda s: re.sub(r"\s+", " ", str(s)).strip().lower()
            same = (n(llm) == n(hum))
        ph_rows.append({"name": name, "LLM": llm, "human": hum, "scores": sc,
                        "mean_score": float(np.mean(vals)) if vals else None, "llm_eq_human": same})
    steps.append({"index": i, "task": it.get("task"), "source": it.get("source"),
                  "answer": it.get("answer"), "scores": it.get("score") or {},
                  "placeholders": ph_rows})

print(f"steps={len(steps)} · placeholders={sum(len(s['placeholders']) for s in steps)}")

# ---------------------------------------------------------------- per-step / per-dimension
dim_mat = np.array([[s["scores"].get(d, np.nan) for d in DIMS] for s in steps], dtype=float)
dim_mean = np.nanmean(dim_mat, axis=0)
step_total = np.nansum(dim_mat, axis=1)
max_total = 2 * len(DIMS)

# ---------------------------------------------------------------- placeholder level
ph_all = [p for s in steps for p in s["placeholders"]]
scored = [p for p in ph_all if p["mean_score"] is not None]
comparable = [p for p in ph_all if p["llm_eq_human"] is not None]
n_match = sum(1 for p in comparable if p["llm_eq_human"])
# annotator agreement
ann_names = sorted({k for p in scored for k in p["scores"]})
numeric = lambda v: isinstance(v, (int, float))
pair_agree = {}
for i, a in enumerate(ann_names):
    for b in ann_names[i + 1:]:
        pair = [(p["scores"][a], p["scores"][b]) for p in scored
                if numeric(p["scores"].get(a)) and numeric(p["scores"].get(b))]
        if pair:
            pair_agree[f"{a}-{b}"] = float(np.mean([x == y for x, y in pair]))

print(f"placeholders={len(ph_all)} · scored={len(scored)} · LLM==human {n_match}/{len(comparable)}"
      f" ({100*n_match/max(len(comparable),1):.0f}%)")
print(f"dim means: {dict(zip(DIMS, np.round(dim_mean,2)))}")
print(f"annotator pairwise agreement: {pair_agree}")

# ---------------------------------------------------------------- FIG 1: score heatmap
fig, ax = plt.subplots(figsize=(8.6, 6.4))
im = ax.imshow(dim_mat, cmap="RdYlGn", vmin=0, vmax=2, aspect="auto")
ax.set_xticks(range(len(DIMS))); ax.set_xticklabels(DIMS, rotation=35, ha="right")
ax.set_yticks(range(len(steps)))
ax.set_yticklabels([f"{s['index']}. {s['task'][:34]}" for s in steps], fontsize=7.5)
for i in range(len(steps)):
    for j in range(len(DIMS)):
        v = dim_mat[i, j]
        if not np.isnan(v):
            ax.text(j, i, int(v), ha="center", va="center", fontsize=7)
ax.set_title("Per-step Hartree-Fock derivation scores (0–2 per dimension)")
fig.colorbar(im, ax=ax, shrink=0.8, label="score")
fig.tight_layout(); fig.savefig(IMG / "step_score_heatmap.png", dpi=170); plt.close(fig)

# ---------------------------------------------------------------- FIG 2: dimension means + step totals
fig, axes = plt.subplots(1, 2, figsize=(12, 4.4))
axes[0].bar(range(len(DIMS)), dim_mean, color="tab:blue", alpha=0.85)
axes[0].axhline(2, ls=":", color="gray"); axes[0].set_ylim(0, 2.2)
axes[0].set_xticks(range(len(DIMS))); axes[0].set_xticklabels(DIMS, rotation=35, ha="right")
axes[0].set_ylabel("mean score"); axes[0].set_title("Mean score per rubric dimension")
axes[1].bar(range(len(steps)), step_total, color="tab:green", alpha=0.85)
axes[1].axhline(max_total, ls=":", color="gray")
axes[1].set_xlabel("step"); axes[1].set_ylabel("total score / 12")
axes[1].set_title("Per-step total score")
fig.tight_layout(); fig.savefig(IMG / "score_summary.png", dpi=170); plt.close(fig)

# ---------------------------------------------------------------- FIG 3: placeholder LLM vs human
fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.3))
axes[0].bar([0, 1], [n_match, len(comparable) - n_match], color=["tab:green", "tab:red"])
axes[0].set_xticks([0, 1]); axes[0].set_xticklabels(["LLM = human", "LLM ≠ human"])
axes[0].set_ylabel("placeholders"); axes[0].set_title(f"Placeholder agreement (n={len(comparable)})")
ms = [p["mean_score"] for p in scored]
axes[1].hist(ms, bins=np.arange(-0.25, 2.75, 0.5), color="tab:orange", alpha=0.85)
axes[1].set_xlabel("mean annotator score"); axes[1].set_ylabel("placeholders")
axes[1].set_title("Placeholder score distribution (0–2)")
fig.tight_layout(); fig.savefig(IMG / "placeholder_analysis.png", dpi=170); plt.close(fig)

# ---------------------------------------------------------------- FIG 4: annotator agreement
fig, ax = plt.subplots(figsize=(6.2, 5.2))
for i, a in enumerate(ann_names):
    for j, b in enumerate(ann_names):
        if i < j:
            pair = [(p["scores"][a], p["scores"][b]) for p in scored
                    if isinstance(p["scores"].get(a), (int, float)) and isinstance(p["scores"].get(b), (int, float))]
            xs = [x for x, y in pair]; ys = [y for x, y in pair]
            ax.scatter(xs, ys, alpha=0.35, s=18, label=f"{a} vs {b}")
ax.plot([0, 2], [0, 2], "k--", lw=1)
ax.set_xlabel("annotator A score"); ax.set_ylabel("annotator B score")
ax.set_title("Inter-annotator agreement on placeholders"); ax.legend(fontsize=8); ax.grid(True, alpha=0.3)
fig.tight_layout(); fig.savefig(IMG / "annotator_agreement.png", dpi=170); plt.close(fig)

# ---------------------------------------------------------------- FIG 5: source-line coverage
fig, ax = plt.subplots(figsize=(8.6, 4.0))
for k, s in enumerate(steps):
    src = s["source"] or {}
    for f, spans in src.items():
        if not isinstance(spans, list):
            continue
        for sp in spans:
            if isinstance(sp, list) and len(sp) == 2:
                ax.plot([sp[0], sp[1]], [k, k], lw=6, color="tab:blue", alpha=0.6)
ax.set_xlabel("source line in 2111.01152.tex")
ax.set_ylabel("step"); ax.set_title("Extraction map: source-line spans per derivation step")
ax.grid(True, alpha=0.3)
fig.tight_layout(); fig.savefig(IMG / "source_map.png", dpi=170); plt.close(fig)

# ---------------------------------------------------------------- outputs
(OUT / "extracted_steps.json").write_text(json.dumps(
    {"paper": "2111.01152", "branch": meta.get("branch"), "steps": steps}, ensure_ascii=False, indent=2),
    encoding="utf-8")
with (OUT / "placeholder_scores.csv").open("w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh); w.writerow(["step", "placeholder", "LLM", "human", "mean_annotator_score", "llm_eq_human"])
    for s in steps:
        for p in s["placeholders"]:
            w.writerow([s["index"], p["name"], p["LLM"], p["human"], p["mean_score"], p["llm_eq_human"]])

metrics = {
    "task": "Information_002", "paper": "2111.01152", "branch": meta.get("branch"),
    "n_steps": len(steps), "n_placeholders": len(ph_all), "n_scored_placeholders": len(scored),
    "dimension_means": dict(zip(DIMS, [float(x) for x in dim_mean])),
    "step_total_scores": [float(x) for x in step_total], "max_total": max_total,
    "weak_steps": [int(s["index"]) for s, t in zip(steps, step_total) if t <= 8],
    "placeholder_llm_eq_human": {"match": n_match, "comparable": len(comparable),
                                 "rate": n_match / max(len(comparable), 1)},
    "annotator_pairwise_agreement": pair_agree,
}
(OUT / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")

print("\n===== SUMMARY =====")
print("weak steps (total<=8):", metrics["weak_steps"])
print("dim means:", {k: round(v, 2) for k, v in metrics["dimension_means"].items()})
print("placeholder agree rate:", metrics["placeholder_llm_eq_human"])
print("figures ->", [p.name for p in sorted(IMG.glob("*.png"))])
