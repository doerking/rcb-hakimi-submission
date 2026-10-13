"""Compute summary statistics for the report."""
import os
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))

from lcoh_model import compute_lcoh_dict
from plot_africa import (
    _africa_polygons, _in_any_poly, compute_all_africa_lcoh,
    _COUNTRY_ZOOMS_ROW2, _COUNTRY_ZOOMS_ROW3,
)
from africa_grid import generate_africa_grid


def _country_of(cell):
    countries = _africa_polygons()
    pt = (cell["lon"], cell["lat"])
    for name, polys in countries.items():
        if _in_any_poly(pt, polys):
            return name
    return None


def _namibia_stats():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    df = pd.read_csv(os.path.join(root, "data", "hex_final_NA_min.csv"))
    df["lcoh"] = df.apply(compute_lcoh_dict, axis=1)
    return df


def _country_stats():
    cells = generate_africa_grid()
    dr, com = compute_all_africa_lcoh(cells)
    df = pd.DataFrame({
        "lon": [c["lon"] for c in cells],
        "lat": [c["lat"] for c in cells],
        "lcoh_dr": dr,
        "lcoh_commercial": com,
    })
    df["country"] = [_country_of(c) for c in cells]
    by = df.groupby("country").agg(
        n=("lcoh_dr", "size"),
        lcoh_dr_min=("lcoh_dr", "min"),
        lcoh_dr_max=("lcoh_dr", "max"),
        lcoh_dr_mean=("lcoh_dr", "mean"),
        lcoh_com_min=("lcoh_commercial", "min"),
        lcoh_com_max=("lcoh_commercial", "max"),
        lcoh_com_mean=("lcoh_commercial", "mean"),
    ).reset_index()
    return by


if __name__ == "__main__":
    print("=" * 60)
    print("NAMIBIA HEX STATS")
    print("=" * 60)
    na = _namibia_stats()
    print(f"N hexes: {len(na)}")
    print(f"LCOH min  : {na.lcoh.min():.3f} €/kg")
    print(f"LCOH max  : {na.lcoh.max():.3f} €/kg")
    print(f"LCOH mean : {na.lcoh.mean():.3f} €/kg")
    print(f"LCOH std  : {na.lcoh.std():.3f} €/kg")
    print()
    print("Lowest 5:")
    print(na.sort_values("lcoh").head(5)[
        ["hex_id", "lat", "lon", "theo_pv", "theo_wind",
         "grid_dist_km", "ocean_dist_km", "lcoh"]
    ].to_string(index=False))
    print()
    print("Highest 5:")
    print(na.sort_values("lcoh").tail(5)[
        ["hex_id", "lat", "lon", "theo_pv", "theo_wind",
         "grid_dist_km", "ocean_dist_km", "lcoh"]
    ].to_string(index=False))

    print()
    print("=" * 60)
    print("AFRICA-WIDE COUNTRY STATS")
    print("=" * 60)
    cs = _country_stats()
    cols = ["country", "n", "lcoh_dr_mean", "lcoh_dr_min", "lcoh_dr_max",
            "lcoh_com_mean"]
    cs_sorted = cs.sort_values("lcoh_dr_mean")
    print(cs_sorted[cols].to_string(index=False, float_format=lambda x: f"{x:.2f}"))
