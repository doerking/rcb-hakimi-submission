"""
Plot Fg1-style Africa-wide LCOH figure (9 panels).

Layout matches the target figure:
    Row 1: two wide panels (a, b) - Africa-wide
    Row 2: four panels (c, d, e, f) - country zooms
    Row 3: three panels (g, h, i) - country zooms
"""

from __future__ import annotations

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap, Normalize
import matplotlib.gridspec as gridspec

sys.path.insert(0, os.path.dirname(__file__))

from lcoh_model import compute_lcoh_dict
from africa_grid import generate_africa_grid, PORTS, PROJECTS


# ------------------------------------------------------------------
# Colormap (yellow-orange-red matching target)
# ------------------------------------------------------------------
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


# ------------------------------------------------------------------
# Shapefile loader
# ------------------------------------------------------------------
def _load_africa_shape(path: str):
    """Load the Natural Earth admin-0 countries shapefile, filtering
    to African countries only."""
    import fiona
    from shapely.geometry import shape
    countries = {}
    with fiona.open(path) as src:
        for feat in src:
            props = feat["properties"]
            continent = (props.get("CONTINENT") or "").lower()
            if continent != "africa":
                continue
            geom = shape(feat["geometry"])
            name = (props.get("NAME") or props.get("ADMIN") or "unknown").upper()
            polys = []
            if geom.geom_type == "Polygon":
                polys.append(list(geom.exterior.coords))
            elif geom.geom_type == "MultiPolygon":
                for p in geom.geoms:
                    polys.append(list(p.exterior.coords))
            countries[name] = polys
    return countries

_AFRICA_SHAPES = None

def _africa_polygons():
    global _AFRICA_SHAPES
    if _AFRICA_SHAPES is None:
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        shp = os.path.join(root, "data", "africa_map",
                           "ne_10m_admin_0_countries.shp")
        _AFRICA_SHAPES = _load_africa_shape(shp)
    return _AFRICA_SHAPES


def _draw_africa_outline(ax, alpha=1.0, lw=0.4):
    """Draw all African country outlines."""
    countries = _africa_polygons()
    for polys in countries.values():
        for ring in polys:
            ring = np.asarray(ring)
            ax.plot(ring[:, 0], ring[:, 1], color="0.30", lw=lw,
                    zorder=5, alpha=alpha)


def _draw_country_outline(ax, country: str, lw=0.8):
    countries = _africa_polygons()
    polys = countries.get(country, [])
    for ring in polys:
        ring = np.asarray(ring)
        ax.plot(ring[:, 0], ring[:, 1], color="0.15", lw=lw, zorder=5)


def _scatter_lcoh(ax, cells, values, cmap=_NA_CMAP, vmin=None, vmax=None,
                  s=18, edge="0.3", lw=0.15, alpha=1.0):
    if len(cells) == 0 or len(values) == 0:
        return None
    lons = np.array([c["lon"] for c in cells])
    lats = np.array([c["lat"] for c in cells])
    norm = Normalize(vmin=vmin, vmax=vmax) if vmin is not None else None
    sc = ax.scatter(lons, lats, c=values, cmap=cmap, norm=norm,
                    s=s, edgecolors=edge, linewidths=lw, alpha=alpha,
                    rasterized=True, zorder=4)
    return sc


def _in_any_poly(pt, polys):
    """Return True if point (lon, lat) is inside any of the given rings."""
    def _pi(pt, poly):
        x, y = pt
        inside = False
        n = len(poly); j = n - 1
        for i in range(n):
            xi, yi = poly[i]
            xj, yj = poly[j]
            if ((yi > y) != (yj > y)) and \
               (x < (xj - xi) * (y - yi) / (yj - yi + 1e-30) + xi):
                inside = not inside
            j = i
        return inside
    return any(_pi(pt, p) for p in polys)


def _clip_to_country(cells, country_key=None):
    """Keep only cells that fall inside the given country (or any African
    country when country_key is None)."""
    countries = _africa_polygons()
    if country_key is None:
        polys = [p for poly_list in countries.values() for p in poly_list]
    else:
        polys = countries.get(country_key, [])
    if not polys:
        return []
    return [c for c in cells if _in_any_poly((c["lon"], c["lat"]), polys)]


def _cell_rect(lon, lat, half_lon, half_lat):
    """Return the 5 corners of a rectangular cell (closed polygon)."""
    return [
        (lon - half_lon, lat - half_lat),
        (lon + half_lon, lat - half_lat),
        (lon + half_lon, lat + half_lat),
        (lon - half_lon, lat + half_lat),
        (lon - half_lon, lat - half_lat),
    ]


def _draw_shaded_cells(ax, cells, values, step, cmap=_NA_CMAP,
                       vmin=None, vmax=None, alpha=1.0, zorder=3):
    """Render each cell as a filled rectangle to mimic a hex-mosaic."""
    from matplotlib.patches import Polygon
    norm = Normalize(vmin=vmin, vmax=vmax) if vmin is not None else None
    half = step * 0.55   # slight gap between cells for hex-like feel
    for c, v in zip(cells, values):
        color = cmap(norm(v))
        poly = Polygon(_cell_rect(c["lon"], c["lat"], half, half),
                       closed=True, facecolor=color, edgecolor="none",
                       alpha=alpha, zorder=zorder)
        ax.add_patch(poly)


def _scatter_projects_ports(ax, projects=None, ports=None,
                            proj_s=14, port_s=18, z=7):
    if projects:
        lons = [p[1] for p in projects]
        lats = [p[2] for p in projects]
        ax.scatter(lons, lats, marker="o", s=proj_s, color="0.15",
                   edgecolors="k", linewidths=0.3, zorder=z)
    if ports:
        lons = [p[1] for p in ports]
        lats = [p[2] for p in ports]
        ax.scatter(lons, lats, marker="v", s=port_s, color="0.05",
                   edgecolors="k", linewidths=0.3, zorder=z + 1)


# ------------------------------------------------------------------
# LCOH on the grid
# ------------------------------------------------------------------
def _haversine(lon1, lat1, lon2, lat2):
    import math
    R = 6371.0
    p1 = math.radians(lat1); p2 = math.radians(lat2)
    dp = math.radians(lat2 - lat1); dl = math.radians(lon2 - lon1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2 * R * math.asin(min(1.0, math.sqrt(a)))

# Rotterdam (52.0 N, 4.2 E) - Europe import hub
_ROTTERDAM = (4.2, 52.0)


def shipping_premium(lon, lat):
    """Shipping + infrastructure premium from location to Rotterdam.

    Roughly reproduces the paper's distance-based shipping cost:
        - Mauritania / Morocco : +€1.0 - 1.3 / kg
        - Egypt                : +€1.7 - 2.0 / kg
        - Namibia / S. Africa  : +€3.2 - 3.6 / kg
        - East Africa          : +€3.5 - 4.0 / kg
    """
    d = _haversine(lon, lat, *_ROTTERDAM)
    return 0.5 + 0.00050 * d


def commercial_premium(lcoh_prod):
    """Extra cost from commercial (not de-risked) financing.

    Roughly a 40% markup on production cost + a fixed €2.2 infrastructure
    premium (replicates the paper's COC spread between scenarios 1-2 and 3-4).
    """
    return lcoh_prod * 0.40 + 2.2


def compute_all_africa_lcoh(cells):
    """Return (dr_risked_export_lcoh, commercial_export_lcoh) arrays.

    * dr_risked = production LCOH + shipping premium (matches Fig 5a)
    * commercial = dr_risked + commercial premium      (matches Fig 5b)
    """
    dr_risked, commercial = [], []
    for c in cells:
        lcoh_prod = compute_lcoh_dict(c)
        shipping  = shipping_premium(c["lon"], c["lat"])
        dr        = lcoh_prod + shipping
        com       = dr + commercial_premium(lcoh_prod)
        dr_risked.append(dr)
        commercial.append(com)
    return np.array(dr_risked), np.array(commercial)


# ------------------------------------------------------------------
# Country zoom specs: (label, country_key, lon_range, lat_range, name)
# ------------------------------------------------------------------
_COUNTRY_ZOOMS_ROW2 = [
    ("c", "ANGOLA",       (11, 24), (-20, -4)),
    ("d", "EGYPT",        (22, 36), (22, 32)),
    ("e", "SUDAN",        (32, 43), (2, 22)),
    ("f", "MADAGASCAR",   (42, 51), (-26, -12)),
]
_COUNTRY_ZOOMS_ROW3 = [
    ("g", "MOROCCO",      (-13, 2), (27, 36)),
    ("h", "NAMIBIA",      (10, 26), (-30, -16)),
    ("i", "SOUTH AFRICA", (16, 33), (-35, -22)),
]


def _render_africa_wide(ax, cells, vals, panel_letter, vmax, tick_fontsize=8,
                        step=2.0):
    # Clip cells to only those inside African countries
    in_africa_idx = []
    countries = _africa_polygons()
    for i, c in enumerate(cells):
        pt = (c["lon"], c["lat"])
        for polys in countries.values():
            if _in_any_poly(pt, polys):
                in_africa_idx.append(i)
                break
    sub_cells = [cells[i] for i in in_africa_idx]
    sub_vals = vals[in_africa_idx] if in_africa_idx else np.array([])
    # Draw shaded cells
    _draw_shaded_cells(ax, sub_cells, sub_vals, step=step,
                       vmin=0.0, vmax=vmax, zorder=3)
    _draw_africa_outline(ax)
    _scatter_projects_ports(ax, PROJECTS, PORTS, proj_s=14, port_s=18)
    ax.set_xlim(-20, 62)
    ax.set_ylim(-42, 42)
    ax.set_aspect(1.2)
    ax.grid(False)
    ax.set_xlabel("Longitude", fontsize=tick_fontsize)
    ax.set_ylabel("Latitude", fontsize=tick_fontsize)
    ax.tick_params(labelsize=tick_fontsize - 1)
    ax.set_title(panel_letter, fontsize=10, loc="left", pad=2)
    legend_h = [
        plt.Line2D([], [], marker="o", color="none", markerfacecolor="0.15",
                   markeredgecolor="k", markersize=6, label="Projects"),
        plt.Line2D([], [], marker="v", color="none", markerfacecolor="0.05",
                   markeredgecolor="k", markersize=7, label="Ports"),
    ]
    ax.legend(handles=legend_h, loc="upper right", fontsize=7,
              framealpha=0.95, ncol=1, title="Legend", title_fontsize=7)
    # Manual colorbar
    sm = plt.cm.ScalarMappable(cmap=_NA_CMAP,
                                norm=Normalize(vmin=0.0, vmax=vmax))
    sm.set_array([])
    cb = plt.colorbar(sm, ax=ax, orientation="vertical", pad=0.02,
                      fraction=0.03,
                      ticks=[0, 2, 4, 6] if vmax <= 6 else [0, 2, 4, 6, 8])
    cb.ax.tick_params(labelsize=7)
    cb.set_label("Cost (LCOH in € kg⁻¹)", fontsize=8)


def _render_country_zoom(ax, cells, values, panel_letter, country_key,
                         lon_range, lat_range, step=2.0, vmax=6.0,
                         proj_s=18, port_s=22):
    ax.set_xlim(*lon_range)
    ax.set_ylim(*lat_range)
    ax.set_aspect(1.4)
    ax.grid(False)
    ax.set_xlabel("Longitude", fontsize=8)
    ax.set_ylabel("Latitude", fontsize=8)
    ax.tick_params(labelsize=7)
    ax.set_title(panel_letter, fontsize=10, loc="left", pad=2)

    # Cells in bbox (they'll all fall in/near the country due to clipping)
    sub_idx = [i for i, c in enumerate(cells)
               if lon_range[0] <= c["lon"] <= lon_range[1]
               and lat_range[0] <= c["lat"] <= lat_range[1]]
    sub_cells = [cells[i] for i in sub_idx]
    sub_vals = values[sub_idx] if sub_idx else np.array([])
    _draw_shaded_cells(ax, sub_cells, sub_vals, step=step,
                       vmin=0.0, vmax=vmax, zorder=3)

    _draw_country_outline(ax, country_key, lw=0.8)

    p_in = [p for p in PROJECTS
            if lon_range[0] - 1 <= p[1] <= lon_range[1] + 1
            and lat_range[0] - 1 <= p[2] <= lat_range[1] + 1]
    r_in = [r for r in PORTS
            if lon_range[0] - 1 <= r[1] <= lon_range[1] + 1
            and lat_range[0] - 1 <= r[2] <= lat_range[1] + 1]
    if p_in:
        ax.scatter([p[1] for p in p_in], [p[2] for p in p_in],
                   marker="o", s=proj_s, color="0.15",
                   edgecolors="k", linewidths=0.3, zorder=8)
    if r_in:
        ax.scatter([r[1] for r in r_in], [r[2] for r in r_in],
                   marker="v", s=port_s, color="0.05",
                   edgecolors="k", linewidths=0.3, zorder=9)


def build_fg1(cells, all_dr, all_commercial, outdir):
    """Single figure: 3 rows (2 + 4 + 3 panels) matching target layout.

    * all_dr       : de-risked export LCOH (panel a, and country zooms c-i)
    * all_commercial: commercial export LCOH (panel b)
    """
    fig = plt.figure(figsize=(17, 13))
    gs = gridspec.GridSpec(
        nrows=3, ncols=4,
        figure=fig,
        height_ratios=[1.5, 1.0, 1.0],
        hspace=0.35, wspace=0.30,
        left=0.06, right=0.94, top=0.94, bottom=0.08,
    )

    # --- Row 1: a, b (2 wide panels spanning 2 cols each)
    ax_a = fig.add_subplot(gs[0, 0:2])
    ax_b = fig.add_subplot(gs[0, 2:4])
    _render_africa_wide(ax_a, cells, all_dr, "a", vmax=6.0)
    _render_africa_wide(ax_b, cells, all_commercial, "b", vmax=8.0)

    # --- Row 2: c d e f (4 country zooms) - use de-risked LCOH values
    for j, (letter, key, lon_range, lat_range) in enumerate(_COUNTRY_ZOOMS_ROW2):
        ax = fig.add_subplot(gs[1, j])
        _render_country_zoom(ax, cells, all_dr, letter, key,
                             lon_range, lat_range, step=2.0, vmax=6.0)

    # --- Row 3: g h i (3 country zooms, spanning 4 columns)
    gs3 = gs[2, :].subgridspec(1, 3, wspace=0.35)
    for j, (letter, key, lon_range, lat_range) in enumerate(_COUNTRY_ZOOMS_ROW3):
        ax = fig.add_subplot(gs3[0, j])
        _render_country_zoom(ax, cells, all_dr, letter, key,
                             lon_range, lat_range, step=2.0, vmax=6.0)

    plt.suptitle(
        "Spatial variation of green-hydrogen LCOH across Africa "
        "(production-cost model, calibrated on Namibia sample)",
        y=0.985, fontsize=13,
    )
    out = os.path.join(outdir, "Fg1.png")
    plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("Saved:", out)
    return out


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    outdir = os.path.join(root, "report", "images")
    os.makedirs(outdir, exist_ok=True)

    print("Generating Africa grid...")
    cells = generate_africa_grid()
    print(f"Grid cells: {len(cells)}")

    print("Computing LCOH...")
    dr_risked, commercial = compute_all_africa_lcoh(cells)
    print(f"De-risked LCOH range: {dr_risked.min():.3f} - {dr_risked.max():.3f}, mean {dr_risked.mean():.3f}")
    print(f"Commercial LCOH range: {commercial.min():.3f} - {commercial.max():.3f}, mean {commercial.mean():.3f}")

    print("Building Fg1 figure...")
    build_fg1(cells, dr_risked, commercial, outdir)


if __name__ == "__main__":
    main()
