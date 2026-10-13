"""
Earth_000 — Reproduce Extended Fig. 3 (regional method comparison).

The target figure shows, for each of the 19 GTN-G regions, the specific
mass-change rate (m w.e. yr⁻¹) as observed by five methods:
    - glaciological (blue square)
    - DEM differencing (light-blue square)
    - altimetry (orange triangle)
    - gravimetry (red-orange circle)
    - combined GlaMBIE (red cross)

arranged in two columns — left = "altimetry observation period",
right = "gravimetry observation period".

We compute per-dataset rates directly from the GlaMBIE input CSVs, convert
to m w.e. using the unit tag and glacier area, take a coverage-weighted
mean per region × method, and plot as horizontal error bars.

Key numbers reproduced (from checklist §Extended Fig. 3):
  • altimetry − DEM bias:   0.08 ± 0.08 m w.e. yr⁻¹
  • gravimetry − DEM bias:  0.02 ± 0.08 m w.e. yr⁻¹
  • glaciological − DEM:    −0.10 ± 0.10, range −0.61 to +0.53
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import json

ROOT = Path(__file__).resolve().parents[1]
IN = ROOT / "data" / "glambie" / "input"
RES_CAL = ROOT / "data" / "glambie" / "results" / "calendar_years"
OUT = ROOT / "report" / "images"
OUT.mkdir(parents=True, exist_ok=True)

ICE_DENSITY = 0.917   # ice-to-water ratio (for m-of-ice → m w.e.)
Gt_per_km2_per_mw = 0.001  # 1 m w.e. over 1 km² = 1 Mt = 0.001 Gt

# ---------------------------------------------------------------------------
# Region metadata
# ---------------------------------------------------------------------------
REGIONS = [
    ("1",  "alaska",              "Alaska"),
    ("2",  "western_canada_us",   "Western Canada & US"),
    ("3",  "arctic_canada_north", "Arctic Canada North"),
    ("4",  "arctic_canada_south", "Arctic Canada South"),
    ("5",  "greenland_periphery", "Greenland Periphery"),
    ("6",  "iceland",             "Iceland"),
    ("7",  "svalbard",            "Svalbard & Jan Mayen"),
    ("8",  "scandinavia",         "Scandinavia"),
    ("9",  "russian_arctic",      "Russian Arctic"),
    ("10", "north_asia",          "North Asia"),
    ("11", "central_europe",      "Central Europe"),
    ("12", "caucasus_middle_east","Caucasus & Middle East"),
    ("13", "central_asia",        "Central Asia"),
    ("14", "south_asia_west",     "South Asia West"),
    ("15", "south_asia_east",     "South Asia East"),
    ("16", "low_latitudes",       "Low Latitudes"),
    ("17", "southern_andes",      "Southern Andes"),
    ("18", "new_zealand",         "New Zealand"),
    ("19", "antarctic_and_subantarctic", "Antarctic & Subantarctic"),
]
METHODS = ["glaciological", "demdiff", "altimetry", "gravimetry", "combined"]

# Observation windows from target image (fractional years).
ALT_WINDOW = {
    "alaska":(2010.75,2019.75),"western_canada_us":(2012.75,2022.75),
    "arctic_canada_north":(2002.75,2023.75),"arctic_canada_south":(2002.75,2023.75),
    "greenland_periphery":(2002.75,2021.75),"iceland":(2010.75,2019.75),
    "svalbard":(2003.75,2019.75),"scandinavia":(2002.75,2023.75),
    "russian_arctic":(2003.75,2019.75),"north_asia":(2002.75,2023.75),
    "central_europe":(2002.75,2023.75),"caucasus_middle_east":(2002.75,2023.75),
    "central_asia":(2002.75,2020.75),"south_asia_west":(2002.75,2020.75),
    "south_asia_east":(2002.75,2020.75),"low_latitudes":(2003.00,2023.00),
    "southern_andes":(2011.25,2020.25),"new_zealand":(2002.25,2023.25),
    "antarctic_and_subantarctic":(2003.25,2023.25),
}
GRAV_WINDOW = {
    "alaska":(2002.75,2022.75),"western_canada_us":(2002.75,2023.75),
    "arctic_canada_north":(2002.75,2022.75),"arctic_canada_south":(2002.75,2022.75),
    "greenland_periphery":(2002.75,2023.75),"iceland":(2002.75,2022.75),
    "svalbard":(2002.75,2022.75),"scandinavia":(2002.75,2023.75),
    "russian_arctic":(2002.75,2022.75),"north_asia":(2002.75,2023.75),
    "central_europe":(2002.75,2023.75),"caucasus_middle_east":(2002.75,2023.75),
    "central_asia":(2002.75,2023.75),"south_asia_west":(2002.75,2023.75),
    "south_asia_east":(2002.75,2023.75),"low_latitudes":(2003.00,2023.00),
    "southern_andes":(2002.25,2022.25),"new_zealand":(2002.25,2023.25),
    "antarctic_and_subantarctic":(2002.25,2023.25),
}

# ---------------------------------------------------------------------------
# Load input data per region × method and compute specific mass-change rates.
# ---------------------------------------------------------------------------
def load_dataset_rate(path, area_km2=None, window=None):
    """Return mean specific rate (m w.e./yr) and 1-sigma uncertainty.

    If window=(start,end) is given, only the overlap with that window is used.
    """
    df = pd.read_csv(path)
    if df.empty:
        return np.nan, np.nan
    unit = df["unit"].iloc[0]
    if window is not None:
        start, end = window
        # Fraction of each row inside the window
        ov_s = np.maximum(df["start_dates"].astype(float).values, start)
        ov_e = np.minimum(df["end_dates"].astype(float).values, end)
        ov_years = np.clip(ov_e - ov_s, 0, None)
        if ov_years.sum() <= 0:
            return np.nan, np.nan
        # Prorated change and error (assume linear within each row)
        row_years = (df["end_dates"].astype(float) - df["start_dates"].astype(float)).values
        frac = np.where(row_years > 0, ov_years / row_years, 0.0)
        changes = df["changes"].astype(float).values * frac
        errors  = df["errors"].astype(float).values * np.sqrt(frac)
        yrs_total = ov_years.sum()
    else:
        changes = df["changes"].astype(float).values
        errors  = df["errors"].astype(float).values
        yrs_total = (df["end_dates"].astype(float) - df["start_dates"].astype(float)).sum()
    total_change = changes.sum()
    if yrs_total <= 0:
        return np.nan, np.nan
    # convert to m w.e.
    if unit == "mwe":
        total_mwe = total_change
        unc_mwe = np.sqrt((errors**2).sum()) / yrs_total
    elif unit == "m":
        total_mwe = total_change * ICE_DENSITY
        unc_mwe = np.sqrt((errors**2).sum()) * ICE_DENSITY / yrs_total
    elif unit.lower() == "gt":
        if area_km2 is None or area_km2 <= 0:
            return np.nan, np.nan
        total_mwe = total_change / (area_km2 * Gt_per_km2_per_mw)
        unc_mwe = np.sqrt((errors**2).sum()) / (area_km2 * Gt_per_km2_per_mw * yrs_total)
    else:
        return np.nan, np.nan
    rate = total_mwe / yrs_total
    return rate, unc_mwe

def region_area(key):
    """Mean glacier area (km²) over 2000-2023 for a region."""
    idx = [k[0] for k in REGIONS if k[1] == key][0]
    path = RES_CAL / f"{idx}_{key}.csv"
    if path.exists():
        df = pd.read_csv(path)
        return float(df["glacier_area"].mean())
    return None

def region_method_rates(region_key, method, window):
    idx = [k[0] for k in REGIONS if k[1] == region_key][0]
    d = IN / f"{idx}_{region_key}"
    if not d.exists():
        return np.nan, np.nan
    if method == "combined":
        files = list(d.glob("*_combined_*.csv"))
    else:
        files = list(d.glob(f"*_{method}_*.csv"))
    if not files:
        return np.nan, np.nan
    area = region_area(region_key)
    rates, uncs, weights = [], [], []
    start, end = window
    for f in files:
        df_probe = pd.read_csv(f)
        if df_probe.empty: continue
        r, u = load_dataset_rate(f, area_km2=area, window=window)
        if not np.isfinite(r):
            continue
        rates.append(r); uncs.append(u)
        # coverage weight = overlap years of the dataset with the window
        df_probe = pd.read_csv(f)
        if df_probe.empty:
            weights.append(1.0)
        else:
            ov_s = max(df_probe["start_dates"].iloc[0], start)
            ov_e = min(df_probe["end_dates"].iloc[-1], end)
            weights.append(max(ov_e - ov_s, 1e-3))
    if not rates:
        return np.nan, np.nan
    w = np.array(weights); r = np.array(rates); u = np.array(uncs)
    rate_mean = float(np.average(r, weights=w))
    # uncertainty: quadrature of weighted standard error
    unc_mean = float(np.sqrt(np.sum(u**2 * w) / w.sum() / w.sum()))
    return rate_mean, unc_mean

def aggregate_for_column(window_by_region):
    out = {}
    for idx, key, label in REGIONS:
        w = window_by_region[key]
        row = {}
        for m in METHODS:
            r, u = region_method_rates(key, m, w)
            row[m] = (r, u)
        row["window"] = w
        out[label] = row
    return out

alt_agg  = aggregate_for_column(ALT_WINDOW)
grav_agg = aggregate_for_column(GRAV_WINDOW)

# ---------------------------------------------------------------------------
# Plot Extended Fig. 3 style
# ---------------------------------------------------------------------------
markers = {"glaciological":("s","steelblue"),
           "demdiff":      ("s","skyblue"),
           "altimetry":    ("^","darkorange"),
           "gravimetry":   ("o","crimson"),
           "combined":     ("+", "red")}
markersize = {"glaciological":10,"demdiff":11,"altimetry":9,"gravimetry":9,"combined":18}
zorder = {"glaciological":3,"demdiff":2,"altimetry":4,"gravimetry":5,"combined":6}

fig, axes = plt.subplots(len(REGIONS), 2,
                         figsize=(11, 0.55 * len(REGIONS)),
                         gridspec_kw={"width_ratios":[1,1], "hspace":0.15})

for i, (idx, key, label) in enumerate(REGIONS):
    for j, (agg, title) in enumerate([(alt_agg,"Altimetry observation period"),
                                       (grav_agg,"Gravimetry observation period")]):
        ax = axes[i, j]
        row = agg[label]
        for m in METHODS:
            r, u = row[m]
            mk, col = markers[m]
            if np.isfinite(r):
                ax.errorbar([r], [i+0.5], xerr=[u] if np.isfinite(u) else [0],
                            fmt=mk, color=col, markersize=markersize[m],
                            capsize=3, linewidth=1.4, zorder=zorder[m])
        w = row["window"]
        ax.text(0.98, 0.05, f"{w[0]:.2f}–{w[1]:.2f}", transform=ax.transAxes,
                ha="right", va="bottom", fontsize=7, color="#555")
        ax.axvline(0, color="k", linewidth=0.6)
        ax.set_xlim(-2.5, 1.5)
        ax.set_ylim(0.4, 1.1)
        ax.tick_params(axis="x", labelsize=7)
        ax.set_yticks([])
        ax.grid(alpha=0.15)
        if i == 0:
            ax.set_title(title, fontsize=10, weight="bold")
        if j == 0:
            ax.set_ylabel(label, fontsize=8)
            ax.tick_params(axis="y", labelleft=True)
        else:
            ax.set_ylabel("")
            ax.tick_params(axis="y", labelleft=False)
        if i < len(REGIONS) - 1:
            ax.tick_params(axis="x", labelbottom=False)

axes[-1, 0].set_xlabel("Mass change rate (m w.e. yr$^{-1}$)", fontsize=9)
axes[-1, 1].set_xlabel("Mass change rate (m w.e. yr$^{-1}$)", fontsize=9)

handles = [mpl.lines.Line2D([0],[0], marker=mk, color=col, ls="",
                            markersize=markersize[m], label=m)
           for m, (mk, col) in markers.items()]
fig.legend(handles=handles, loc="lower center", ncol=5, fontsize=9, frameon=False,
           bbox_to_anchor=(0.5, -0.02))

fig.suptitle("Extended Fig. 3 — Regional specific mass-change rate by method\n"
             "(GlaMBIE 2000–2023)", fontsize=12, y=0.995)
fig.tight_layout(rect=[0, 0.02, 1, 0.98])
fig.savefig(OUT / "extend_fig3_regional_methods.png", dpi=170, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------------------
# Cross-method biases
# ---------------------------------------------------------------------------
def diff(agg, method_a, method_b="demdiff"):
    out = []
    for _, _, label in REGIONS:
        row = agg[label]
        a = row[method_a][0]
        b = row[method_b][0]
        if np.isfinite(a) and np.isfinite(b):
            out.append(a - b)
    return out

biases = {
    "alt_vs_dem":   diff(alt_agg, "altimetry"),
    "grav_vs_dem":  diff(grav_agg, "gravimetry"),
    "glac_vs_dem":  diff(alt_agg, "glaciological"),
}
def stat(arr):
    if not arr:
        return None
    a = np.array(arr)
    return {"n":int(len(a)),
            "mean":round(float(a.mean()),3),
            "err": round(float(a.std(ddof=1)/np.sqrt(len(a))),3),
            "min": round(float(a.min()),3),
            "max": round(float(a.max()),3)}

summary = {k: stat(v) for k, v in biases.items()}
print("=== Cross-method biases (m w.e./yr) ===")
for k, v in summary.items():
    print(f"  {k:12s} {v}")
print("\nPaper target:  alt-DEM = 0.08±0.08, grav-DEM = 0.02±0.08, glac-DEM = -0.10±0.10, range -0.61 to +0.53")

(ROOT / "outputs" / "method_biases.json").write_text(json.dumps(summary, indent=2))
print("Figure:", OUT / "extend_fig3_regional_methods.png")
