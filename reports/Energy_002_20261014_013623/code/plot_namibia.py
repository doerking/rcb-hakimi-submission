"""
Plot the Namibia hex LCOH scatter (image 2, target:
min_lcoh_map_NA_2023_with_contour.png).

Reads data/hex_final_NA_min.csv (30 hexes), computes LCOH using the
model calibrated in lcoh_model.py, and produces a scatter-map overlay
on the Namibia outline.

Colourbar: 1.35 - 1.60 €/kg (matches the target exactly).
"""

from __future__ import annotations

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, Normalize

sys.path.insert(0, os.path.dirname(__file__))

from lcoh_model import compute_lcoh_dict

# Same colormap as the Africa-wide figure (yellow -> dark red)
_NA_CMAP = LinearSegmentedColormap.from_list(
    "namibia_lcoh",
    [
        (1.0, 1.0, 0.85),   # light yellow
        (1.0, 0.85, 0.35),  # orange-yellow
        (1.0, 0.55, 0.15),  # orange
        (0.90, 0.20, 0.15), # red
        (0.55, 0.05, 0.10), # dark red
        (0.35, 0.00, 0.05), # very dark red
    ],
)


def _load_namibia_outline(shape_path: str):
    """Load just the Namibia polygon from the shapefile."""
    import fiona
    from shapely.geometry import shape
    rings = []
    with fiona.open(shape_path) as src:
        for feat in src:
            props = feat["properties"]
            if (props.get("CONTINENT") or "").lower() != "africa":
                continue
            name = (props.get("NAME") or "").upper()
            if name != "NAMIBIA":
                continue
            geom = shape(feat["geometry"])
            if geom.geom_type == "Polygon":
                rings.append(list(geom.exterior.coords))
            elif geom.geom_type == "MultiPolygon":
                for p in geom.geoms:
                    rings.append(list(p.exterior.coords))
    return rings


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    shp = os.path.join(root, "data", "africa_map",
                       "ne_10m_admin_0_countries.shp")
    csv = os.path.join(root, "data", "hex_final_NA_min.csv")
    outdir = os.path.join(root, "report", "images")
    os.makedirs(outdir, exist_ok=True)

    # Load hex data
    df = pd.read_csv(csv)
    df["lcoh"] = df.apply(compute_lcoh_dict, axis=1)
    print(f"Loaded {len(df)} hexes, LCOH range {df['lcoh'].min():.3f} - "
          f"{df['lcoh'].max():.3f} (mean {df['lcoh'].mean():.3f})")

    # Load Namibia outline
    namibia_rings = _load_namibia_outline(shp)
    print(f"Namibia outline: {len(namibia_rings)} ring(s)")

    # Build figure
    fig, ax = plt.subplots(figsize=(9, 10))

    # Draw Namibia outline (background)
    for ring in namibia_rings:
        arr = np.asarray(ring)
        ax.plot(arr[:, 0], arr[:, 1], color="0.35", lw=1.2, zorder=1)
        ax.fill(arr[:, 0], arr[:, 1], color="0.93", zorder=0)

    # Compute colorbar range: match target 1.35-1.60
    vmin, vmax = 1.35, 1.60

    # Draw hex scatter
    sc = ax.scatter(
        df["lon"], df["lat"],
        c=df["lcoh"],
        cmap=_NA_CMAP,
        norm=Normalize(vmin=vmin, vmax=vmax),
        s=200, edgecolors="0.15", linewidths=0.6, alpha=0.95,
        rasterized=True, zorder=5,
    )

    # Axes (matching target style)
    ax.set_xlim(8, 27)
    ax.set_ylim(-32, -14)
    ax.set_aspect("equal")
    ax.grid(True, ls=":", alpha=0.4, zorder=1)
    ax.set_xlabel("Longitude", fontsize=11, labelpad=8)
    ax.set_ylabel("Latitude", fontsize=11, labelpad=8)
    ax.set_title(
        "Spatial variation of green hydrogen cost (Namibia, 2023)",
        fontsize=13, pad=10,
    )

    # Colourbar
    cb = plt.colorbar(sc, ax=ax, orientation="vertical", pad=0.02,
                      fraction=0.035,
                      ticks=[1.35, 1.40, 1.45, 1.50, 1.55, 1.60])
    cb.ax.tick_params(labelsize=9)
    cb.set_label("LCOH (€/kg)", fontsize=10)

    plt.tight_layout()
    out = os.path.join(outdir, "min_lcoh_map_NA_2023_with_contour.png")
    plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved: {out}")

    # Also save the underlying LCOH per hex for report reference
    out_csv = os.path.join(outdir, "namibia_lcoh_per_hex.csv")
    df[["hex_id", "lat", "lon", "theo_pv", "theo_wind",
        "grid_dist_km", "road_dist_km", "ocean_dist_km",
        "waterbody_dist_km", "lcoh"]].to_csv(out_csv, index=False)
    print(f"Saved hex-level data: {out_csv}")


if __name__ == "__main__":
    main()
