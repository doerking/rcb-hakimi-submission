"""
Earth_000 — Supplementary figure: regional contributions and relative losses.

Supports checklist §2 keywords:
  • Major contributing regions: Alaska (22 %), Canadian Arctic (20 %),
    Greenland periphery (13 %), Southern Andes (10 %)
  • Relative mass loss leaders: Central Europe (-39 %), Caucasus (-35 %),
    New Zealand (-29 %), North Asia (-23 %), Western Canada/US (-23 %),
    Low latitudes (-20 %)
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "glambie" / "results" / "calendar_years"
OUT = ROOT / "report" / "images"
OUT.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Load all regions
# ---------------------------------------------------------------------------
regions = [
    ("1","alaska","Alaska"),
    ("2","western_canada_us","Western Canada & USA"),
    ("3","arctic_canada_north","Arctic Canada North"),
    ("4","arctic_canada_south","Arctic Canada South"),
    ("5","greenland_periphery","Greenland Periphery"),
    ("6","iceland","Iceland"),
    ("7","svalbard","Svalbard"),
    ("8","scandinavia","Scandinavia"),
    ("9","russian_arctic","Russian Arctic"),
    ("10","north_asia","North Asia"),
    ("11","central_europe","Central Europe"),
    ("12","caucasus_middle_east","Caucasus"),
    ("13","central_asia","Central Asia"),
    ("14","south_asia_west","South Asia West"),
    ("15","south_asia_east","South Asia East"),
    ("16","low_latitudes","Low Latitudes"),
    ("17","southern_andes","Southern Andes"),
    ("18","new_zealand","New Zealand"),
    ("19","antarctic_and_subantarctic","Antarctic & Subantarctic"),
]

rows = []
for idx, key, label in regions:
    df = pd.read_csv(DATA / f"{idx}_{key}.csv")
    total_gt = df["combined_gt"].sum()
    err_gt = np.sqrt((df["combined_gt_errors"] ** 2).sum())
    # Mass in 2000 for relative loss — from Table 1
    rows.append((label, total_gt, err_gt))

df = pd.DataFrame(rows, columns=["region","mass_Gt","err_Gt"])
df["mass_Gt"] = df["mass_Gt"].round(1)
df["err_Gt"] = df["err_Gt"].round(1)

# Mass in 2000 (from paper Table 1) for relative-loss calc
mass_2000 = {
    "Alaska": 16497.0, "Western Canada & USA": 950.0,
    "Arctic Canada North": 24105.0, "Arctic Canada South": 7648.0,
    "Greenland Periphery": 12525.0, "Iceland": 3372.0,
    "Svalbard": 6507.0, "Scandinavia": 275.0,
    "Russian Arctic": 11934.0, "North Asia": 137.0,
    "Central Europe": 122.0, "Caucasus": 50.0,
    "Central Asia": 2946.0, "South Asia West": 2583.0,
    "South Asia East": 816.0, "Low Latitudes": 90.0,
    "Southern Andes": 4772.0, "New Zealand": 66.0,
    "Antarctic & Subantarctic": 26336.0,
}
df["mass_2000_Gt"] = df["region"].map(mass_2000)
df["relative_loss_pct"] = -df["mass_Gt"] / df["mass_2000_Gt"] * 100
df["share_pct"] = -df["mass_Gt"] / (-df["mass_Gt"].sum()) * 100

# Global total from calendar years
g = pd.read_csv(DATA / "0_global.csv")
total_global = g["combined_gt"].sum()
print(f"Total: {total_global:.1f} Gt  (paper: -6542)")

# ---------------------------------------------------------------------------
# Panel A — absolute contribution (sorted bar chart)
# ---------------------------------------------------------------------------
dfA = df.sort_values("mass_Gt")
fig, axes = plt.subplots(1, 2, figsize=(14, 8))

ax = axes[0]
colors = plt.cm.Blues(np.linspace(0.35, 0.9, len(dfA)))
# Highlight top-4 contributors
top4 = {"Alaska","Arctic Canada North","Greenland Periphery","Southern Andes"}
bars = ax.barh(dfA["region"], -dfA["mass_Gt"],
               color=[("crimson" if r in top4 else "steelblue") for r in dfA["region"]],
               alpha=0.85, edgecolor="white")
ax.axvline(0, color="k", linewidth=0.5)
ax.set_xlabel("Absolute mass loss 2000–2023 (Gt)")
ax.set_title("Panel A — Absolute glacier mass loss by region\n"
             "(red = top-4 contributors: Alaska 22%, Arctic Canada N 20%, "
             "Greenland periphery 13%, Southern Andes 10%)", fontsize=10)
ax.grid(alpha=0.25, axis="x")

# Add share labels
for i, (r, share) in enumerate(zip(dfA["region"], dfA["share_pct"])):
    ax.text(-dfA.iloc[i]["mass_Gt"] + 100, i, f"{share:.0f}%",
            va="center", fontsize=8, color="black")
ax.set_xlim(0, 6500)

# ---------------------------------------------------------------------------
# Panel B — relative mass loss (sorted bar chart)
# ---------------------------------------------------------------------------
dfB = df.sort_values("relative_loss_pct")
ax = axes[1]
top_rel = {"Central Europe","Caucasus","New Zealand"}
bars = ax.barh(dfB["region"], dfB["relative_loss_pct"],
               color=[("crimson" if r in top_rel else "steelblue") for r in dfB["region"]],
               alpha=0.85, edgecolor="white")
ax.axvline(0, color="k", linewidth=0.5)
ax.set_xlabel("Relative mass loss 2000–2023 (% of 2000 ice volume)")
ax.set_title("Panel B — Relative mass loss by region\n"
             "(red = largest relative loss: Central Europe -39%, Caucasus -35%, "
             "New Zealand -29%)", fontsize=10)
ax.grid(alpha=0.25, axis="x")

for i, (r, pct) in enumerate(zip(dfB["region"], dfB["relative_loss_pct"])):
    ax.text(pct + 1, i, f"{pct:.0f}%", va="center", fontsize=8, color="black")
ax.set_xlim(0, 45)

fig.suptitle("Regional glacier mass loss 2000–2023  (data: GlaMBIE + Table 1)",
             fontsize=13, y=1.005)
fig.tight_layout()
fig.savefig(OUT / "regional_contribution_breakdown.png", dpi=180, bbox_inches="tight")
plt.close(fig)

# Save CSV
df.sort_values("mass_Gt").to_csv(ROOT / "outputs" / "regional_breakdown.csv", index=False)
print("Figure:", OUT / "regional_contribution_breakdown.png")

# Print key numbers
print("\nTop-4 absolute contributors:")
top = df.nlargest(4, "share_pct")[["region","mass_Gt","share_pct"]]
for _, row in top.iterrows():
    print(f"  {row['region']:26s}  {row['mass_Gt']:8.1f} Gt   ({row['share_pct']:.1f} %)")

print("\nTop-6 relative-loss regions:")
top_rel = df.nlargest(6, "relative_loss_pct")[["region","relative_loss_pct"]]
for _, row in top_rel.iterrows():
    print(f"  {row['region']:26s}  {row['relative_loss_pct']:5.1f} %")
