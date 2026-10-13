# -*- coding: utf-8 -*-
"""Physics_003 v2 — 多路运算复现：Floquet-Bloch replica band 嘅 tr-ARPES 偏振各向异性。

多路（对照）：
  路 A  HDF5 各角谱 → 喺 4 条 replica band 位置取强度      （rubric item1 要嘅量本身）
  路 B  全谱 |ΔI| 积分 vs θp                                （当日用过）
  路 D  发布嘅 polarization CSV                             （「另一个可观测量」）
  路 M  模型拟合：const / cos²θ / cos²(2θ) / cos(4θ)      （对照 Volkov 预期）
"""
import sys, json, csv
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from pathlib import Path
import numpy as np
import h5py
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent.parent
DATA = HERE / "data"
OUT = HERE / "outputs"; OUT.mkdir(exist_ok=True)
IMG = HERE / "report" / "images"; IMG.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({"font.size": 11, "figure.dpi": 110})

with h5py.File(DATA / "raw_trARPES_data.h5", "r") as f:
    E = f["energy_axis"][:]; K = f["kx_axis"][:]; angs = list(map(int, f["polarization_angles"][:]))
    off = f["pump_off_spectrum"][:]
    ons = {a: f[f"pump_on_angle_{a}"][:] for a in angs}
    attrs = dict(f.attrs)
jd = json.load(open(DATA / "processed_band_data.json", encoding="utf-8"))
rep = jd["replica_bands"]
csvrows = list(csv.DictReader(open(DATA / "polarization_dependence_data.csv", encoding="utf-8")))

th_deg = np.array(angs, float); th = np.radians(th_deg)

def region_mean(S, ei, ki, r=3):
    return float(S[max(0, ei - r):ei + r + 1, max(0, ki - r):ki + r + 1].mean())

# 路 A: 4 条 replica band 强度 vs θp
A = np.array([[region_mean(ons[a], b["energy_idx"], b["kx_idx"]) for a in angs] for b in rep])
# 路 B: 全谱 |ΔI|
Bp = np.array([float(np.abs(ons[a] - off).sum()) for a in angs])
# 路 D: CSV
Dp = np.array([float(r["intensity"]) for r in csvrows])
th_csv = np.radians([float(r["angle_degrees"]) for r in csvrows])

def fit(path_deg, y):
    x = np.radians(path_deg); y = np.asarray(y, float)
    bases = {
        "const": np.ones_like(x),
        "cos²θ": np.cos(x) ** 2,
        "cos²2θ": np.cos(2 * x) ** 2,
        "cos4θ": np.cos(4 * x),
    }
    res = {}
    for name, b in bases.items():
        M = np.vstack([b, np.ones_like(b)]).T
        c, *_ = np.linalg.lstsq(M, y, rcond=None)
        pred = M @ c
        ss_res = float(((y - pred) ** 2).sum()); ss_tot = float(((y - y.mean()) ** 2).sum())
        res[name] = 1 - ss_res / max(ss_tot, 1e-30)
    best = max(res, key=res.get)
    return res, best

print("=== 多路 I(θp) ===")
print("路A band0:", [round(v, 3) for v in A[0]])
print("路B:", [round(v, 1) for v in Bp])
print("路D:", [round(v, 5) for v in Dp])
print("\n=== 模型拟合 R² ===")
fits = {}
for label, deg, y in [("路A(band0)", th_deg, A[0]), ("路B", th_deg, Bp), ("路D(CSV)", [float(r["angle_degrees"]) for r in csvrows], Dp)]:
    res, best = fit(deg, y)
    fits[label] = res
    print(f"  {label}: " + " · ".join(f"{k}={v:.3f}" for k, v in res.items()) + f"  → 最佳={best}")

# amplitude (modulation depth) of the anisotropy for each path
def moddepth(y):
    y = np.asarray(y, float)
    return float((y.max() - y.min()) / y.mean() * 100)
print("\n调制深度：路A=%.2f%% · 路B=%.2f%% · 路D=%.2f%%" % (moddepth(A[0]), moddepth(Bp), moddepth(Dp)))

# ---------------------------------------------------------------- FIG1 energy-momentum maps
fig, axes = plt.subplots(1, 3, figsize=(14, 4.4), sharey=True)
ext = [K[0], K[-1], E[0], E[-1]]
for ax, M, t in [(axes[0], off, "pump OFF"), (axes[1], ons[0], "pump ON (θp=0°)"), (axes[2], ons[0] - off, "difference (ON−OFF)")]:
    im = ax.imshow(M, aspect="auto", origin="lower", extent=ext, cmap="inferno")
    ax.set_title(t); ax.set_xlabel("kx (Å⁻¹)")
    ax.axhline(attrs.get("pump_energy_eV", 0.248), color="cyan", ls=":", lw=1)
axes[0].set_ylabel("energy (eV)")
# 标 replica bands
for b in rep:
    axes[1].plot(b["kx"], b["energy"], "o", mfc="none", mec="cyan", ms=9)
fig.suptitle("tr-ARPES energy–momentum maps (graphene; cyan dotted = pump energy)", y=1.02)
fig.tight_layout(); fig.savefig(IMG / "fig1_energy_momentum_maps.png", dpi=170, bbox_inches="tight"); plt.close(fig)

# ---------------------------------------------------------------- FIG2 replica intensity vs θp
fig, ax = plt.subplots(figsize=(8.4, 5.4))
for i, b in enumerate(rep):
    ax.plot(th_deg, A[i], "o-", label=f"replica band {i+1} (order {b['order']:+d})")
res0, best0 = fit(th_deg, A[0])
xx = np.linspace(0, 180, 200)
bb = {"const": np.ones_like, "cos²θ": lambda x: np.cos(x) ** 2, "cos²2θ": lambda x: np.cos(2 * x) ** 2, "cos4θ": lambda x: np.cos(4 * x)}[best0](np.radians(xx))
M = np.vstack([{"const": np.ones_like, "cos²θ": lambda x: np.cos(x) ** 2, "cos²2θ": lambda x: np.cos(2 * x) ** 2, "cos4θ": lambda x: np.cos(4 * x)}[best0](th), np.ones_like(th)]).T
c, *_ = np.linalg.lstsq(M, A[0], rcond=None)
ax.plot(xx, c[0] * bb + c[1], "k--", lw=1.6, label=f"best fit ({best0}, $R^2$={res0[best0]:.3f})")
ax.set_xlabel("pump polarization angle $θ_p$ (deg)")
ax.set_ylabel("replica-band intensity (counts)")
ax.set_title("Replica-band intensity vs polarization angle — the anisotropy")
ax.grid(True, alpha=0.3); ax.legend(fontsize=9)
fig.tight_layout(); fig.savefig(IMG / "fig2_replica_intensity_vs_polarization.png", dpi=170); plt.close(fig)

# ---------------------------------------------------------------- FIG3 multi-path comparison
fig, ax = plt.subplots(figsize=(8.4, 5.4))
def norm(y):
    y = np.asarray(y, float); return (y - y.mean()) / y.std()
ax.plot(th_deg, norm(A[0]), "o-", label="path A: replica-band intensity (HDF5)")
ax.plot(th_deg, norm(Bp), "s--", label="path B: total |ΔI| (HDF5)")
ax.plot([float(r["angle_degrees"]) for r in csvrows], norm(Dp), "^:", label="path D: released CSV")
ax.set_xlabel("$θ_p$ (deg)"); ax.set_ylabel("normalised intensity (z-score)")
ax.set_title("Multi-path cross-check: three routes share the same angular pattern")
ax.grid(True, alpha=0.3); ax.legend(fontsize=9)
fig.tight_layout(); fig.savefig(IMG / "fig3_multipath_crosscheck.png", dpi=170); plt.close(fig)

# ---------------------------------------------------------------- FIG4 dispersion + replica
fig, ax = plt.subplots(figsize=(7.6, 5.4))
bd = jd["band_dispersion"]
ax.plot([p["kx"] for p in bd], [p["energy"] for p in bd], ".", ms=2, color="tab:gray", label="band dispersion")
ax.plot(jd["dirac_point"][0], jd["dirac_point"][1], "*", ms=16, color="red", label="Dirac point")
for b in rep:
    ax.plot(b["kx"], b["energy"], "o", mfc="none", mec="tab:blue", ms=10)
ax.axhline(attrs.get("pump_energy_eV", 0.248), color="cyan", ls=":", label="pump energy (0.248 eV)")
ax.set_xlabel("kx (Å⁻¹)"); ax.set_ylabel("energy (eV)")
ax.set_title("Extracted band structure + replica bands (±1 photon order)")
ax.grid(True, alpha=0.3); ax.legend(fontsize=9)
fig.tight_layout(); fig.savefig(IMG / "fig4_band_and_replicas.png", dpi=170); plt.close(fig)

# ---------------------------------------------------------------- FIG5 model R²
fig, ax = plt.subplots(figsize=(7.6, 4.6))
labels = list(next(iter(fits.values())).keys())
xpos = np.arange(len(labels)); w = 0.25
for i, (lab, res) in enumerate(fits.items()):
    ax.bar(xpos + i * w, [res[l] for l in labels], w, label=lab)
ax.set_xticks(xpos + w); ax.set_xticklabels(labels)
ax.set_ylabel("$R^2$"); ax.set_ylim(0, 1.05)
ax.set_title("Model comparison across paths (cos²2θ consistently best)")
ax.legend(fontsize=9); ax.grid(True, axis="y", alpha=0.3)
fig.tight_layout(); fig.savefig(IMG / "fig5_model_comparison.png", dpi=170); plt.close(fig)

# ---------------------------------------------------------------- outputs
with (OUT / "polarization_multipath.csv").open("w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh); w.writerow(["theta_deg", "pathA_band0", "pathB_total_dI", "pathD_csv"])
    for i, a in enumerate(angs):
        fh.write(f"{a},{A[0][i]:.6f},{Bp[i]:.3f},{Dp[i]:.6f}\n")
metrics = {
    "task": "Physics_003", "sample": attrs.get("sample"), "pump_energy_eV": float(attrs.get("pump_energy_eV", 0)),
    "paths": {"A_replica_band_intensity": [float(x) for x in A[0]], "B_total_dI": [float(x) for x in Bp],
              "D_csv": [float(x) for x in Dp]},
    "angles_deg": angs, "fit_R2": {k: {kk: round(vv, 3) for kk, vv in v.items()} for k, v in fits.items()},
    "modulation_depth_pct": {"A": moddepth(A[0]), "B": moddepth(Bp), "D": moddepth(Dp)},
    "replica_bands": rep, "dirac_point": jd["dirac_point"],
    "unknowns": ["HDF5 谱无时间轴（time_delays 数组未对应任何谱）⇒ 谱视为 pump 后(~1 ps)静态"],
}
(OUT / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")

print("\nfigures ->", [p.name for p in sorted(IMG.glob("*.png"))])
