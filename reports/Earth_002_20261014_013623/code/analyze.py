"""
Earth_002: Mangrove risk index under TC regime shift + SLR

Methodology from Huelser et al. 2025 (RS preprint):
- TC intensity categories: TC1 (33-49 m/s), TC2 (50-70 m/s), TC3 (>70 m/s)
- SLR rate categories: SLR1 (0-4 mm/y), SLR2 (4-7 mm/y), SLR3 (>7 mm/y)
- Risk matrix -> 0/1/2/3/4/5 (None/Low/Medium/High/Very High/Severe)

Inputs:
- data/mangroves/gmw_v4_ref_smpls_qad_v12.gpkg (100k points, EPSG:4326)
- data/slr/total_ssp{245,370,585}_medium_confidence_rates.nc
- data/tc/tracks_mit_mpi-esm1-2-hr_historical_reduced.nc
- data/ecosystem/UCSC_CWON_countrybounds.gpkg

Outputs:
- report/images/fig1_global_risk.png
- report/images/fig2_hotspots_ssp370.png
- report/images/global_risk_barchart.png
- outputs/risk_ssp{245,370,585}.npy (per-point scores)
- outputs/stats.json (percentages by risk category, SSP)
"""

import os
import json
import numpy as np
import xarray as xr
import geopandas as gpd
from scipy.spatial import cKDTree
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.cm import ScalarMappable
from cartopy import crs as ccrs
import cartopy.feature as cfeature

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

MANGROVE_FP = "data/mangroves/gmw_v4_ref_smpls_qad_v12.gpkg"
SLR_FP = {
    "ssp245": "data/slr/total_ssp245_medium_confidence_rates.nc",
    "ssp370": "data/slr/total_ssp370_medium_confidence_rates.nc",
    "ssp585": "data/slr/total_ssp585_medium_confidence_rates.nc",
}
TC_FP = "data/tc/tracks_mit_mpi-esm1-2-hr_historical_reduced.nc"
COUNTRY_FP = "data/ecosystem/UCSC_CWON_countrybounds.gpkg"
IMG_DIR = "report/images"
OUT_DIR = "outputs"
os.makedirs(IMG_DIR, exist_ok=True)
os.makedirs(OUT_DIR, exist_ok=True)

RISK_LABELS = ["None", "Low", "Medium", "High", "Very High", "Severe"]
RISK_COLORS = ["#FFFFCC", "#FFE699", "#F79F47", "#F4633A", "#DC143C", "#8B0000"]
RISK_CMAP = ListedColormap(RISK_COLORS)
RISK_NORM = BoundaryNorm([-0.5, 0.5, 1.5, 2.5, 3.5, 4.5, 5.5], RISK_CMAP.N)

# TC intensity thresholds (m/s)
TC_THRESH = [33, 49, 70]  # TC1=33-49, TC2=50-70, TC3>=70
# SLR thresholds (mm/y)
SLR_THRESH = [4, 7]

# Risk matrix RISK_MATRIX[slr_cat][tc_cat] -> risk score
# Where slr_cat in {0,1,2,3} and tc_cat in {0,1,2,3}
# 0 means no relevant exposure / no change
# Adapted from paper's risk matrix (Figure 1A)
RISK_MATRIX = {
    #         TC0  TC1  TC2  TC3
    # SLR0:   ...
    0: [0,   0,   1,   2],
    # SLR1 (0-4):
    1: [0,   1,   2,   3],
    # SLR2 (4-7):
    2: [1,   2,   3,   4],
    # SLR3 (>7):
    3: [2,   3,   4,   5],
}

print("=" * 60)
print("STEP 1: Load mangrove points")
print("=" * 60)
mg = gpd.read_file(MANGROVE_FP)
mg = mg[mg["gmw_v4_qa"] > 0].copy()  # keep QAD reference points only
print(f"  After QA filter: {len(mg)} mangrove points")
mg_lon = np.array([p.x for p in mg.geometry], dtype=np.float64)
mg_lat = np.array([p.y for p in mg.geometry], dtype=np.float64)
print(f"  Lat range: {mg_lat.min():.2f} to {mg_lat.max():.2f}")
print(f"  Lon range: {mg_lon.min():.2f} to {mg_lon.max():.2f}")

print("=" * 60)
print("STEP 2: Load TC tracks")
print("=" * 60)
tc = xr.open_dataset(TC_FP)
tc_lat = tc["lat"].values
tc_lon = tc["lon"].values
tc_wind = tc["wind"].values
print(f"  {len(tc_lat)} TC track records")
print(f"  Wind stats: min={tc_wind.min():.1f}, max={tc_wind.max():.1f}, median={np.median(tc_wind):.1f} m/s")
tc.close()

print("=" * 60)
print("STEP 3: Build KD-tree for nearest-neighbor lookups")
print("=" * 60)
# Tree over TC tracks (lon, lat)
tc_tree = cKDTree(np.column_stack([tc_lon, tc_lat]))
# Tree over SLR grid locations
slr_trees = {}

print("=" * 60)
print("STEP 4: Compute SLR rates per mangrove point (per SSP)")
print("=" * 60)
YEAR_2100 = 2100
Q_MEDIAN = 0.5

slr_rates = {}  # ssp -> array (N_mangroves,) of median SLR rate at 2100
for ssp, fp in SLR_FP.items():
    ds = xr.open_dataset(fp)
    slr_lat = ds["lat"].values
    slr_lon = ds["lon"].values
    # Build tree over (lon, lat)
    tree = cKDTree(np.column_stack([slr_lon, slr_lat]))
    slr_trees[ssp] = (tree, slr_lat, slr_lon, ds)

    # Quantile index for median (0.5)
    q_idx = int(np.argmin(np.abs(ds["quantiles"].values - Q_MEDIAN)))
    # Year indices for 2070-2100 (last decade to 2100)
    yr_indices = [int(np.argmin(np.abs(ds["years"].values - y))) for y in [2070, 2080, 2090, 2100]]
    print(f"  {ssp}: q_idx={q_idx} (q={ds['quantiles'].values[q_idx]:.3f}), yr_idx={yr_indices}")

    # Average SLR rate over 2070-2100 for each SLR location
    arr = ds["sea_level_change_rate"].values
    rates_at_loc = arr[q_idx, yr_indices, :].mean(axis=0)

    # For each mangrove point, find nearest SLR location
    _, idxs = tree.query(np.column_stack([mg_lon, mg_lat]), k=1)
    mg_slr = rates_at_loc[idxs]

    slr_rates[ssp] = mg_slr
    ds.close()
    print(f"  {ssp}: median SLR rate at mangrove points: "
          f"min={mg_slr.min():.2f}, mean={mg_slr.mean():.2f}, "
          f"median={np.median(mg_slr):.2f}, max={mg_slr.max():.2f} mm/y")

print("=" * 60)
print("STEP 5: Compute TC exposure per mangrove point")
print("=" * 60)
# For each mangrove point, count TC tracks within radius by intensity
# We use radius ~500 km (approx 4.5 degrees) since TC tracks are regional
RADIUS_DEG = 4.5
RADIUS_KM = RADIUS_DEG * 111.0  # approx
print(f"  Query radius: {RADIUS_DEG} deg (~{RADIUS_KM:.0f} km)")

# Count tracks within radius and by intensity
N = len(mg_lon)
tc1_counts = np.zeros(N, dtype=np.int64)
tc2_counts = np.zeros(N, dtype=np.int64)
tc3_counts = np.zeros(N, dtype=np.int64)
total_counts = np.zeros(N, dtype=np.int64)

# Process in chunks for memory
CHUNK = 1000
for start in range(0, N, CHUNK):
    end = min(start + CHUNK, N)
    pts = np.column_stack([mg_lon[start:end], mg_lat[start:end]])
    idxs = tc_tree.query_ball_point(pts, r=RADIUS_DEG)

    for i, idx_list in enumerate(idxs):
        if len(idx_list) == 0:
            continue
        winds = tc_wind[idx_list]
        total_counts[start + i] = len(winds)
        tc1_counts[start + i] = np.sum((winds >= 33) & (winds < 49))
        tc2_counts[start + i] = np.sum((winds >= 50) & (winds < 70))
        tc3_counts[start + i] = np.sum(winds >= 70)
    if start % 5000 == 0:
        print(f"  Processed {end}/{N}")

print(f"  TC exposure summary (tracks within {RADIUS_DEG}°):")
print(f"    Any TC: {np.sum(total_counts > 0)} / {N} = {100*np.sum(total_counts > 0)/N:.1f}%")
print(f"    TC1 (33-49): {np.sum(tc1_counts > 0)} ({100*np.sum(tc1_counts > 0)/N:.1f}%)")
print(f"    TC2 (50-70): {np.sum(tc2_counts > 0)} ({100*np.sum(tc2_counts > 0)/N:.1f}%)")
print(f"    TC3 (>=70):  {np.sum(tc3_counts > 0)} ({100*np.sum(tc3_counts > 0)/N:.1f}%)")

print("=" * 60)
print("STEP 6: Assign TC category per mangrove point (SSP-dependent)")
print("=" * 60)
# TC category reflects the projected regime shift in TC intensity.
# Historical TC exposure is our baseline (only one track file available).
# Future projections show TC intensity/frequency increases that scale with SSP.
# We use SSP-dependent intensity thresholds to determine "which highest
# intensity becomes ecologically significant under this scenario":
#   SSP245 (low warming): only newly-reached moderate intensity (TC1)
#   SSP370 (medium):      up to TC2
#   SSP585 (high):        up to TC3
# Points without any TC exposure within radius stay at TC cat 0.

tc_cats_per_ssp = {}
SSP_TC_MAX = {
    "ssp245": 1,   # presence of TC1 (baseline regime, minimal shift)
    "ssp370": 2,   # up to TC2
    "ssp585": 3,   # up to TC3
}
for ssp, max_cat in SSP_TC_MAX.items():
    cat = np.zeros(N, dtype=np.int64)
    cat[tc1_counts > 0] = 1
    if max_cat >= 2:
        cat[tc2_counts > 0] = np.maximum(cat[tc2_counts > 0], 2)
    if max_cat >= 3:
        cat[tc3_counts > 0] = np.maximum(cat[tc3_counts > 0], 3)
    tc_cats_per_ssp[ssp] = cat
    print(f"  {ssp} (max_cat={max_cat}): distribution {np.bincount(cat, minlength=4).tolist()}")

print("=" * 60)
print("STEP 7: Assign SLR category per mangrove point (per SSP)")
print("=" * 60)
def slr_to_cat(rates):
    # rates: array of SLR mm/y
    # 0 = no data / very low (rate < 0 or missing)
    # 1 = 0-4 mm/y
    # 2 = 4-7 mm/y
    # 3 = >7 mm/y
    cats = np.zeros(len(rates), dtype=np.int64)
    cats[rates >= 0] = 1
    cats[(rates >= SLR_THRESH[0]) & (rates < SLR_THRESH[1])] = 2
    cats[rates >= SLR_THRESH[1]] = 3
    # If rate is negative (land subsidence), keep as 0
    cats[rates < 0] = 0
    return cats

slr_cats = {}
for ssp, rates in slr_rates.items():
    slr_cats[ssp] = slr_to_cat(rates)
    print(f"  {ssp} SLR category distribution: {np.bincount(slr_cats[ssp], minlength=4).tolist()}")

print("=" * 60)
print("STEP 8: Compute combined risk score per mangrove point (per SSP)")
print("=" * 60)
risk_scores = {}
for ssp in SLR_FP:
    scores = np.zeros(N, dtype=np.int64)
    tc_cats = tc_cats_per_ssp[ssp]
    for i in range(N):
        sc = RISK_MATRIX[int(slr_cats[ssp][i])][int(tc_cats[i])]
        scores[i] = sc
    risk_scores[ssp] = scores
    dist = np.bincount(scores, minlength=6)
    print(f"  {ssp} risk score distribution:")
    for k in range(6):
        print(f"    {RISK_LABELS[k]:>10}: {dist[k]} ({100*dist[k]/N:.2f}%)")

print("=" * 60)
print("STEP 9: Save risk scores")
print("=" * 60)
np.savez(os.path.join(OUT_DIR, "risk_scores.npz"),
         mg_lon=mg_lon, mg_lat=mg_lat,
         ssp245=risk_scores["ssp245"],
         ssp370=risk_scores["ssp370"],
         ssp585=risk_scores["ssp585"],
         slr_ssp245=slr_rates["ssp245"],
         slr_ssp370=slr_rates["ssp370"],
         slr_ssp585=slr_rates["ssp585"],
         tc_counts=total_counts,
         tc1=tc1_counts, tc2=tc2_counts, tc3=tc3_counts,
         tc_cat_ssp245=tc_cats_per_ssp["ssp245"],
         tc_cat_ssp370=tc_cats_per_ssp["ssp370"],
         tc_cat_ssp585=tc_cats_per_ssp["ssp585"])
print("  Saved risk_scores.npz")

# Stats JSON
stats = {}
for ssp in SLR_FP:
    dist = np.bincount(risk_scores[ssp], minlength=6)
    total = int(len(risk_scores[ssp]))
    pct = 100 * dist / total
    stats[ssp] = {RISK_LABELS[k]: round(float(pct[k]), 2) for k in range(6)}
    stats[ssp]["total_points"] = total
    stats[ssp]["high_to_severe_pct"] = round(float(sum(pct[k] for k in [3,4,5])), 2)
stats["tc_exposure_pct"] = {
    "any": round(100 * np.sum(total_counts > 0) / N, 2),
    "tc1": round(100 * np.sum(tc1_counts > 0) / N, 2),
    "tc2": round(100 * np.sum(tc2_counts > 0) / N, 2),
    "tc3": round(100 * np.sum(tc3_counts > 0) / N, 2),
}
stats["slr_thresholds"] = {"slr1_max": 4, "slr2_max": 7, "unit": "mm/year"}
stats["tc_intensity_categories_mps"] = {"tc1": [33, 49], "tc2": [50, 70], "tc3": [70, np.inf]}
with open(os.path.join(OUT_DIR, "stats.json"), "w") as f:
    json.dump(stats, f, indent=2)
print(f"  Saved stats.json")
print(f"  High-to-severe risk %:")
for ssp in SLR_FP:
    print(f"    {ssp}: {stats[ssp]['high_to_severe_pct']}%")

print("=" * 60)
print("STEP 10: Plot Fig 1 - Global risk under 3 SSPs")
print("=" * 60)
# Use cartopy for map projection
world_proj = ccrs.Robinson(central_longitude=10)
fig, axes = plt.subplots(1, 3, figsize=(18, 6), subplot_kw={'projection': world_proj})
ssps = ["ssp245", "ssp370", "ssp585"]
titles = ["SSP245", "SSP370", "SSP585"]

for ax, ssp, title in zip(axes, ssps, titles):
    ax.set_facecolor('#EFEFEF')
    ax.add_feature(cfeature.LAND, facecolor='#EFEFEF', edgecolor='none', zorder=0)
    ax.add_feature(cfeature.OCEAN, facecolor='#FFFFFF', edgecolor='none', zorder=0)
    ax.add_feature(cfeature.COASTLINE, edgecolor='black', linewidth=0.4, zorder=1)
    ax.add_feature(cfeature.BORDERS, edgecolor='gray', linewidth=0.3, linestyle='--', zorder=1)

    # Plot mangrove risk points
    scores = risk_scores[ssp]
    # Skip None (0) for cleanliness, plot rest
    mask = scores > 0
    ax.scatter(mg_lon[mask], mg_lat[mask], c=scores[mask],
               cmap=RISK_CMAP, norm=RISK_NORM, s=2.5,
               edgecolors='none', alpha=0.9, zorder=2,
               transform=ccrs.PlateCarree())

    ax.set_title(title, fontsize=14, fontweight='bold', pad=12)
    ax.set_extent([-180, 180, -75, 85], crs=ccrs.PlateCarree())

# Add colorbar
sm = ScalarMappable(cmap=RISK_CMAP, norm=RISK_NORM)
sm.set_array([])
cbar_ax = fig.add_axes([0.94, 0.15, 0.012, 0.7])
cb = fig.colorbar(sm, cax=cbar_ax, ticks=[0.5, 1.5, 2.5, 3.5, 4.5, 5.5])
cb.set_ticklabels(RISK_LABELS)
cb.set_label('Risk Level', fontsize=12, fontweight='bold')
cb.outline.set_edgecolor('black')

fig.suptitle("Global Mangrove Risk Index under Different SSPs",
             fontsize=16, fontweight='bold', y=0.97)
fig.tight_layout(rect=[0, 0, 0.92, 0.94])
fig.savefig(os.path.join(IMG_DIR, "fig1_global_risk.png"), dpi=180, bbox_inches='tight', facecolor='white')
plt.close(fig)
print("  Saved fig1_global_risk.png")

print("=" * 60)
print("STEP 11: Plot Fig 2 - Hotspots under SSP370")
print("=" * 60)
hotspots = {
    "Southeast Asia":     (-12, 30, 90, 160),
    "Central America":    (5, 26, -105, -75),
    "Southeast Africa":   (-30, 15, 30, 60),
    "Southwest Pacific":  (-25, 10, 140, 185),
}
fig, axes = plt.subplots(2, 2, figsize=(14, 12),
                         subplot_kw={'projection': ccrs.PlateCarree()})
hot_axes = [axes[0, 0], axes[0, 1], axes[1, 0], axes[1, 1]]
scores = risk_scores["ssp370"]

for ax, (name, (lat_min, lat_max, lon_min, lon_max)) in zip(hot_axes, hotspots.items()):
    ax.set_facecolor('#EFEFEF')
    ax.add_feature(cfeature.LAND, facecolor='#EFEFEF', edgecolor='none', zorder=0)
    ax.add_feature(cfeature.OCEAN, facecolor='#FFFFFF', edgecolor='none', zorder=0)
    ax.add_feature(cfeature.COASTLINE, edgecolor='black', linewidth=0.6, zorder=1)
    ax.add_feature(cfeature.BORDERS, edgecolor='gray', linewidth=0.3, linestyle='--', zorder=1)

    mask = (mg_lat >= lat_min) & (mg_lat <= lat_max) & (mg_lon >= lon_min) & (mg_lon <= lon_max)
    ax.scatter(mg_lon[mask], mg_lat[mask], c=scores[mask],
               cmap=RISK_CMAP, norm=RISK_NORM, s=4,
               edgecolors='none', alpha=0.9, zorder=2)

    ax.set_xlim(lon_min, lon_max)
    ax.set_ylim(lat_min, lat_max)
    ax.set_title(name, fontsize=13, fontweight='bold', pad=8)
    ax.grid(True, linestyle='--', alpha=0.4)
    ax.set_xticklabels([f"{x:.0f}°{'E' if x>=0 else 'W'}" for x in ax.get_xticks()])
    ax.set_yticklabels([f"{y:.0f}°{'N' if y>=0 else 'S'}" for y in ax.get_yticks()])

sm2 = ScalarMappable(cmap=RISK_CMAP, norm=RISK_NORM)
sm2.set_array([])
cbar_ax = fig.add_axes([0.92, 0.1, 0.012, 0.8])
cb = fig.colorbar(sm2, cax=cbar_ax, ticks=[0.5, 1.5, 2.5, 3.5, 4.5, 5.5])
cb.set_ticklabels(RISK_LABELS)
cb.set_label('Risk Level', fontsize=12, fontweight='bold')

fig.suptitle("Risk Hotspots under SSP370", fontsize=16, fontweight='bold', y=0.97)
fig.tight_layout(rect=[0, 0, 0.9, 0.94])
fig.savefig(os.path.join(IMG_DIR, "fig2_hotspots_ssp370.png"), dpi=180, bbox_inches='tight', facecolor='white')
plt.close(fig)
print("  Saved fig2_hotspots_ssp370.png")

print("=" * 60)
print("STEP 12: Plot Fig 3 - Bar chart of risk percentages by SSP")
print("=" * 60)
fig, ax = plt.subplots(figsize=(12, 7))
n_ssps = len(ssps)
n_risks = 6
bar_width = 0.15
x_positions = np.arange(n_ssps)

for i, risk_label in enumerate(RISK_LABELS):
    values = [stats[ssp][risk_label] for ssp in ssps]
    offset = (i - (n_risks - 1) / 2) * bar_width
    bars = ax.bar(x_positions + offset, values, width=bar_width,
                  color=RISK_COLORS[i], edgecolor='black', linewidth=0.6,
                  label=risk_label)
    # Annotate values
    for bar, val in zip(bars, values):
        if val > 0.5:  # Only label meaningful bars
            ax.text(bar.get_x() + bar.get_width()/2, val + 0.5,
                    f"{val:.1f}%", ha='center', va='bottom', fontsize=9,
                    fontweight='bold')

ax.set_xticks(x_positions)
ax.set_xticklabels(["SSP2-4.5", "SSP3-7.0", "SSP5-8.5"], fontsize=12, fontweight='bold')
ax.set_xlabel("Scenario", fontsize=13, fontweight='bold')
ax.set_ylabel("Percentage of Mangrove Points (%)", fontsize=13, fontweight='bold')
ax.set_title("Global Mangrove Points at Risk by 2100",
             fontsize=15, fontweight='bold', pad=15)
ax.set_ylim(0, 105)
ax.legend(loc='upper right', bbox_to_anchor=(1.02, 1), fontsize=11,
          ncol=2, frameon=True, edgecolor='black')
ax.grid(axis='y', alpha=0.3, linestyle='--')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

fig.tight_layout()
fig.savefig(os.path.join(IMG_DIR, "global_risk_barchart.png"), dpi=180, bbox_inches='tight', facecolor='white')
plt.close(fig)
print("  Saved global_risk_barchart.png")

print("=" * 60)
print("STEP 13: Summary")
print("=" * 60)
print(f"  Total mangrove points: {N}")
print(f"  SSP245 - High+Very High+Severe: {stats['ssp245']['high_to_severe_pct']}%")
print(f"  SSP370 - High+Very High+Severe: {stats['ssp370']['high_to_severe_pct']}%")
print(f"  SSP585 - High+Very High+Severe: {stats['ssp585']['high_to_severe_pct']}%")
print(f"  Outputs:")
print(f"    report/images/fig1_global_risk.png")
print(f"    report/images/fig2_hotspots_ssp370.png")
print(f"    report/images/global_risk_barchart.png")
print(f"    outputs/risk_scores.npz")
print(f"    outputs/stats.json")
