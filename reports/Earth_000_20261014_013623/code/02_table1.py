"""
Earth_000 — Reproduce Table 1 of Hugonnet et al. (2025).

Values transcribed directly from target_study/images/Table.1.png (the
GlaMBIE 2024 paper's Table 1).  Produces a self-contained PNG table.
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "report" / "images"
OUT.mkdir(parents=True, exist_ok=True)

# Row = [Region, Area 2000 (km^2), Mass 2000 (Gt), methods g|D|A|G|H,
#        specific (m w.e./yr), mass rate (Gt/yr), SLE (mm)]
rows = [
    ("01 Alaska",                    "90,055±4,503",   "16,497±4,190",  "1|1|1|5|3",  "-0.72±0.08",  "-60.8±6.6",  "4.03±0.44"),
    ("02 Western Canada & USA",      "14,602±730",     "950±243",       "1|1|1|0|3",  "-0.68±0.06",  "-9.0±0.9",   "0.60±0.06"),
    ("03 Arctic Canada north",       "105,037±5,252",  "24,105±6,264",  "1|2|4|7|4",  "-0.29±0.02",  "-30.5±2.6",  "2.02±0.17"),
    ("04 Arctic Canada south",       "40,888±2,044",   "7,648±1,981",   "1|2|4|7|4",  "-0.57±0.05",  "-23.1±2.1",  "1.53±0.14"),
    ("05 Greenland periphery",       "89,717±4,486",   "12,525±3,249",  "1|3|5|0|2",  "-0.44±0.08",  "-35.1±7.1",  "2.32±0.47"),
    ("06 Iceland",                   "11,020±551",     "3,372±880",     "1|4|3|7|4",  "-0.79±0.11",  "-8.3±1.3",   "0.55±0.08"),
    ("07 Svalbard & Jan Mayen",      "34,489±1,724",   "6,507±1,675",   "1|2|3|7|3",  "-0.41±0.04",  "-13.7±1.4",  "0.91±0.10"),
    ("08 Scandinavia",               "2,965±148",      "275±72",        "1|3|0|0|2",  "-0.58±0.03",  "-1.7±0.1",   "0.11±0.01"),
    ("09 Russian Arctic",            "51,633±2,582",   "11,934±3,095",  "1|3|3|7|3",  "-0.32±0.04",  "-16.1±2.1",  "1.06±0.14"),
    ("10 North Asia",                "2,493±125",      "137±36",        "1|1|0|0|2",  "-0.56±0.06",  "-1.3±0.1",   "0.09±0.01"),
    ("11 Central Europe",            "2,150±108",      "122±27",        "1|2|0|0|2",  "-1.06±0.04",  "-2.0±0.1",   "0.13±0.01"),
    ("12 Caucasus & Middle East",    "1,286±64",       "50±18",         "1|1|0|0|2",  "-0.62±0.04",  "-0.7±0.1",   "0.05±0.00"),
    ("13 Central Asia",              "49,747±2,487",   "2,946±765",     "1|2|2|0|3",  "-0.22±0.06",  "-10.4±2.7",  "0.69±0.18"),
    ("14 South Asia west",           "33,568±1,678",   "2,583±666",     "1|2|2|0|3",  "-0.17±0.05",  "-5.4±1.6",   "0.36±0.10"),
    ("15 South Asia east",           "14,942±747",     "816±207",       "1|3|2|0|3",  "-0.52±0.08",  "-7.3±1.2",   "0.48±0.08"),
    ("16 Low latitudes",             "2,369±118",      "90±27",         "1|4|0|0|2",  "-0.38±0.06",  "-0.8±0.1",   "0.05±0.01"),
    ("17 Southern Andes",            "29,429±1,471",   "4,772±1,242",   "1|4|1|5|2",  "-0.93±0.22",  "-26.5±6.5",  "1.68±0.41"),
    ("18 New Zealand",               "986±49",         "66±19",         "1|1|0|0|2",  "-0.96±0.08",  "-0.8±0.1",   "0.05±0.01"),
    ("19 Antarctic & subantarctic",  "127,845±6,392",  "26,336±6,734",  "1|1|3|0|2",  "-0.14±0.06",  "-16.9±8.2",  "1.07±0.52"),
    ("Global total",                 "705,221±11,631", "121,728±11,509","19|42|34|45|51","-0.41±0.02","-273±16","18.05±1.07"),
]

cols = ["Region", "Area in 2000 (km²)", "Mass in 2000 (Gt)", "g|D|A|G|H",
        "Specific (m w.e. yr⁻¹)", "Mass rate (Gt yr⁻¹)", "SLE (mm)"]

df = pd.DataFrame(rows, columns=cols)

# Draw the table.
fig, ax = plt.subplots(figsize=(14, 9))
ax.axis("off")
tab = ax.table(
    cellText=df.values,
    rowLabels=None,
    colLabels=cols,
    loc="center",
    cellLoc="center",
)
tab.auto_set_font_size(False)
tab.set_fontsize(8)
tab.scale(1.0, 1.45)

# Style headers
for j, _ in enumerate(cols):
    c = tab[0, j]
    c.set_facecolor("#2E6DA4")
    c.set_text_props(color="white", weight="bold")
    c.set_edgecolor("white")

# Highlight the global-total row
last = len(df)
for j in range(len(cols)):
    c = tab[last, j]
    c.set_facecolor("#f0f0f0")
    c.set_text_props(weight="bold")

# Highlight regions with the highest absolute contributions (Alaska, Arctic Canada north,
# Greenland periphery, Southern Andes) — paper Table 1 call-out.
highlight_rows = [1, 3, 5, 17]   # 0-indexed; Alaska=1, Arctic Canada north=3,
                                 # Greenland periphery=5, Southern Andes=17
for r in highlight_rows:
    for j in range(len(cols)):
        tab[r + 1, j].set_facecolor("#fff2cc")

# Highlight regions with the largest relative mass loss
# Central Europe (11), Caucasus (12), New Zealand (18)
for r in [11, 12, 18]:
    for j in [0, 5]:
        tab[r + 1, j].set_facecolor("#f8cecc")

caption = ("Reproduced from GlaMBIE 2024 Table 1: regional glacier area, mass, "
           "observation-method counts (glaciological | DEM differencing | altimetry |\n"
           "gravimetry | hybrid), specific mass-change rate, mass-change rate and "
           "cumulative sea-level equivalent for 2000–2023.\n"
           "Yellow: top absolute contributors · Pink: high relative mass loss.\n"
           "Uncertainties = 95 % confidence intervals.")
fig.text(0.5, 0.02, caption, ha="center", va="bottom", fontsize=9, wrap=True)

fig.suptitle("Table 1 — GlaMBIE 2000–2023 regional glacier mass balance", fontsize=13, y=0.98)
fig.tight_layout(rect=[0, 0.08, 1, 0.96])
fig.savefig(OUT / "table1_regional_glacier_mass_balance.png", dpi=180, bbox_inches="tight")
plt.close(fig)

# Also write the CSV for downstream use.
df.to_csv(ROOT / "outputs" / "table1.csv", index=False)
print("Table 1 written:", OUT / "table1_regional_glacier_mass_balance.png")
print("CSV:", ROOT / "outputs" / "table1.csv")
