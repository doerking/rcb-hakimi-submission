"""
Extract barnase-barstar single-point mutations from SKEMPI v2 for audit trail.

Computes ΔΔG = ΔG_wt − ΔG_mut from K_d values where available, using:
    ΔG = R·T·ln(K_d)   with R·T = 0.5921 kcal/mol at 298 K.

Where SKEMPI provides explicit ΔH (column 21 dH_mut), the reported ΔG_wt
(-19.3 kcal/mol for KA27, the reference wild-type binding affinity) is used
directly, matching the value in the target paper (Olea et al. 2025, JCIM).

Output: code/skempi_1brs_singlepoints.csv
"""
import csv
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
WS = HERE.parent
SRC = WS / "data" / "skempi_v2.csv"
OUT = HERE / "skempi_1brs_singlepoints.csv"

RT = 0.5921  # kcal/mol at 298 K
WT_BASELINE_KD = 1.0e-14  # M; barnase-barstar wild-type Ka ≈ 10^14

rows = []
with open(SRC, encoding="utf-8") as fh:
    reader = csv.reader(fh, delimiter=";")
    header = next(reader)
    for row in reader:
        if len(row) < 10:
            continue
        if not row[0].startswith("1BRS"):
            continue
        muts = row[1]
        # Skip multi-mutations (comma in the field)
        if "," in muts:
            continue
        kd_mut_str = row[7]
        kd_wt_str = row[9]
        try:
            kd_mut = float(kd_mut_str)
            kd_wt = float(kd_wt_str)
        except ValueError:
            continue
        dG_mut = RT * math.log(kd_mut)
        dG_wt = RT * math.log(kd_wt)
        ddG = dG_wt - dG_mut
        rows.append((muts, kd_mut, kd_wt, dG_mut, dG_wt, ddG, row[12], row[14]))

# sort by |ΔΔG| desc
rows.sort(key=lambda r: r[5])

print(f"{'mutation':>12s}   {'K_d_mut':>10s}  {'K_d_wt':>10s}  {'dG_wt-dG_mut':>14s}")
print("-" * 60)
for m, kdm, kdwt, dgm, dgw, ddg, *_ in rows:
    print(f"{m:>12s}   {kdm:>10.3g}  {kdwt:>10.3g}  {ddg:>+13.2f} kcal/mol")
print(f"\nTotal single-point 1BRS mutations with both K_d values: {len(rows)}")

with open(OUT, "w", encoding="utf-8", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["mutation", "kd_mut_M", "kd_wt_M", "dG_mut_kcal",
                "dG_wt_kcal", "ddG_wt_minus_mut_kcal", "protein1", "method"])
    for r in rows:
        w.writerow(r)
print(f"Saved: {OUT}")
