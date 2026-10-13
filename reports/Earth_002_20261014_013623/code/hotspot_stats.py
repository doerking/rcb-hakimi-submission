"""Compute regional hotspot statistics and country-level stats."""
import numpy as np
import geopandas as gpd
import json

data = np.load("outputs/risk_scores.npz", allow_pickle=True)
mg_lon = data["mg_lon"]
mg_lat = data["mg_lat"]
scores = {ssp: data[ssp] for ssp in ["ssp245", "ssp370", "ssp585"]}

REGIONS = {
    "Southeast Asia":      (-12, 30, 90, 160),
    "Central America":     (5, 26, -105, -75),
    "Southeast Africa":    (-30, 15, 30, 60),
    "Southwest Pacific":   (-25, 10, 140, 185),
}

RISK_LABELS = ["None", "Low", "Medium", "High", "Very High", "Severe"]

regional_stats = {}
for name, (lat_min, lat_max, lon_min, lon_max) in REGIONS.items():
    mask = (mg_lat >= lat_min) & (mg_lat <= lat_max) & (mg_lon >= lon_min) & (mg_lon <= lon_max)
    n = int(mask.sum())
    print(f"\n=== {name}: {n} mangrove points ===")
    regional_stats[name] = {"n_points": n}
    for ssp, sc in scores.items():
        dist = np.bincount(sc[mask], minlength=6)
        pct = 100 * dist / n if n > 0 else np.zeros(6)
        high_severe = pct[3] + pct[4] + pct[5]
        severe_only = pct[5]
        print(f"  {ssp}: high+very high+severe = {high_severe:.1f}%, severe only = {severe_only:.1f}%")
        print(f"    Distribution: {[f'{RISK_LABELS[i]}={pct[i]:.1f}%' for i in range(6)]}")
        regional_stats[name][ssp] = {
            "high_to_severe_pct": round(float(high_severe), 2),
            "severe_pct": round(float(severe_only), 2),
            "distribution": {RISK_LABELS[i]: round(float(pct[i]), 2) for i in range(6)}
        }

# Country-level stats (Philippines, Vietnam, Malaysia, Indonesia, Mozambique, Tanzania, Florida)
country_bbs = {
    "Philippines": (5, 20, 117, 127),
    "Vietnam": (8, 24, 102, 110),
    "Malaysia": (0, 7, 100, 119),
    "Indonesia": (-11, 7, 95, 141),
    "Mozambique": (-26, -10, 30, 41),
    "Tanzania": (-11, -1, 30, 41),
    "Florida": (25, 31, -82, -80),
    "Bahamas": (21, 27, -80, -71),
}

country_stats = {}
for name, (lat_min, lat_max, lon_min, lon_max) in country_bbs.items():
    mask = (mg_lat >= lat_min) & (mg_lat <= lat_max) & (mg_lon >= lon_min) & (mg_lon <= lon_max)
    n = int(mask.sum())
    print(f"\n=== {name}: {n} mangrove points ===")
    country_stats[name] = {"n_points": n}
    if n > 0:
        for ssp, sc in scores.items():
            dist = np.bincount(sc[mask], minlength=6)
            pct = 100 * dist / n
            severe_pct = pct[5]
            high_severe = pct[3] + pct[4] + pct[5]
            print(f"  {ssp}: severe = {severe_pct:.1f}%, high+ = {high_severe:.1f}%")
            country_stats[name][ssp] = {
                "severe_pct": round(float(severe_pct), 2),
                "high_to_severe_pct": round(float(high_severe), 2),
            }

# Save
with open("outputs/hotspot_stats.json", "w") as f:
    json.dump({"regions": regional_stats, "countries": country_stats}, f, indent=2)
print("\nSaved outputs/hotspot_stats.json")
