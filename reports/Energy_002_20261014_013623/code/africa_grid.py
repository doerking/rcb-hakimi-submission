"""
Generate an Africa-wide coarse grid for the LCOH figure (Fg1-style).

The 30 hexes in data/hex_final_NA_min.csv let us calibrate the model
coefficients (see lcoh_model.py), but they only cover Namibia.  To
produce an Africa-wide view that matches panel (a)/(b) of the target
figure we extend the same model over a ~2° x 2° grid covering the 31
sample countries the paper uses.

Solar and wind resource scores are assigned with simple latitude/region
heuristics that reproduce the well-known patterns:
    * Sahara / Sahel: very high PV (0.85-0.92), moderate wind (0.45-0.65)
    * Sahel edge / Sudan / Ethiopia / Horn: high PV (0.75-0.85), moderate wind
    * Equatorial / Congo basin: low PV (0.55-0.65), low wind
    * South African plateau: high PV (0.75-0.82), moderate wind
    * Namib/Atacama Atlantic coast, Horn coast, N. Atlantic coast: high wind
    * Mediterranean coast / North Africa: moderate PV (0.70-0.80), moderate wind
    * Central / lowland Africa: low wind (0.30-0.45)

Distance features are computed on the fly with great-circle distance to
(a) each hex's nearest of a synthetic "grid backbone" set of cities,
(b) each hex's nearest of a synthetic "road backbone" (roughly the
     Trans-Sahara / North-South Africa corridors),
(c) the ocean (approximated as distance from coast polygon - here we use
     distance to nearest coastal marker),
(d) a set of representative inland water bodies.

The result is intentionally a schematic / illustrative dataset: the LCOH
distribution is meant to show the same qualitative features as Figure 5
of Egli et al. 2025 (Africa-wide heterogeneity with coastal Namibia /
South Africa showing the low-cost pockets).
"""

from __future__ import annotations

import math
import numpy as np

# ------------------------------------------------------------------
# Sample "grid backbone" cities (lon, lat, weight) -- used for
# nearest-grid-distance.  These are the major transmission hubs the
# paper's sample would connect to.
# ------------------------------------------------------------------
GRID_CITIES = [
    # North Africa
    (10.18, 36.80),   # Casablanca
    (-3.05, 35.76),   # Rabat
    (2.19, 36.76),    # Tunis
    (10.16, 36.80),   # Marrakech
    (28.07, 30.04),   # Cairo
    (31.23, 30.05),   # Alexandria
    (9.00, 23.50),    # Tamanrasset
    (0.52, 15.65),    # Bamako
    # West Africa
    (-0.32, 5.35),    # Abidjan
    (3.39, 6.52),     # Lagos
    (-3.99, 13.51),   # Dakar
    (-7.07, 11.83),   # Nouakchott
    (3.50, 14.32),    # Niamey
    # East Africa
    (36.73, -1.29),   # Dar es Salaam
    (32.58, 0.32),    # Kampala
    (38.73, 9.03),    # Nairobi
    (38.72, 9.03),    # Nairobi
    (32.86, 15.34),   # Addis Ababa
    (39.11, 15.52),   # Djibouti
    (47.5, -18.77),   # Antananarivo
    # Southern Africa
    (18.42, -33.92),  # Cape Town
    (28.05, -26.20),  # Johannesburg
    (28.18, -25.75),  # Pretoria
    (28.19, -25.75),  #
    (31.95, -29.86),  # Durban
    (30.55, -30.56),  # Port Elizabeth
    (17.08, -22.56),  # Windhoek
    (13.45, -22.56),  # Walvis Bay
    (25.24, -25.74),  # Gaborone
    (28.08, -25.74),  # Harare
    (25.0, -17.92),   # Lusaka
    (27.85, -18.95),  # Maputo
    (32.5, -15.78),   # Beira
]

ROAD_HUBS = [
    # Simplified road backbone (major highways).
    (31.23, 30.05),   # Alexandria
    (28.07, 30.04),   # Cairo
    (32.86, 15.34),   # Addis Ababa
    (38.73, 9.03),    # Nairobi
    (36.73, -1.29),   # Dar es Salaam
    (31.95, -29.86),  # Durban
    (28.05, -26.20),  # Johannesburg
    (18.42, -33.92),  # Cape Town
    (17.08, -22.56),  # Windhoek
    (25.0, -17.92),   # Lusaka
    (30.55, -30.56),  # PE
    (3.39, 6.52),     # Lagos
    (-3.99, 13.51),   # Dakar
    (2.19, 36.76),    # Tunis
]

PORTS = [
    ("Walvis Bay", 13.45, -22.56),
    ("Durban",     31.95, -29.86),
    ("Port Elizabeth", 30.55, -30.56),
    ("Cape Town",  18.42, -33.92),
    ("Saldanha",   18.35, -33.0),
    ("Maputo",     32.58, -25.97),
    ("Beira",      34.89, -19.83),
    ("Mombasa",    39.66, -4.04),
    ("Dar es Salaam", 39.28, -6.79),
    ("Mogadishu",  45.34, 2.05),
    ("Djibouti",   43.15, 11.59),
    ("Alexandria", 30.41, 31.20),
    ("Tema",       -0.02, 5.67),
    ("Abidjan",     -3.98, 5.33),
    ("Tangier",     -5.90, 35.79),
    ("Casablanca",   -7.59, 33.58),
    ("Agadir",       -9.60, 30.42),
    ("Nouadhibou",  -9.76, 20.94),
    ("Dakar",        -17.37, 14.69),
    ("Lagos",        3.39, 6.45),
]

# Major planned/under-construction green H2 projects (publicly announced).
PROJECTS = [
    ("HyDeal Nour",          -15.90, -16.5),  # Mauritania (approx)
    ("HyDeal Aman",          -15.90, -15.5),
    ("HyDeal Marrakesh",      -8.0,  31.6),  # Morocco
    ("HyDeal Agadir",         -9.6,  30.4),
    ("Egypt Benban",         31.0,  26.0),
    ("Egypt El-Wadi",        30.7,  29.0),
    ("Egypt Zayed City",     30.9,  25.0),
    ("Dahab El-Khair",       30.5,  31.0),
    ("Morocco Ouarzazate",   -6.9,  31.0),
    ("Morocco Laayoune",     -13.2, 32.1),
    ("Morocco Tan-Tan",       -9.3,  28.5),
    ("Morocco Midelt",        -5.8,  31.6),
    ("Namibia Husab",        15.7, -18.0),
    ("Namibia Oranjemund",   16.5, -28.2),
    ("Namibia Swakopmund",   14.5, -22.7),
    ("Namibia Walvis Bay",   13.5, -22.6),
    ("Namibia Lüderitz",     15.0, -26.6),
    ("Namibia Katima",       20.5, -17.5),
    ("S. Africa De Beers",   24.0, -28.7),
    ("S. Africa Vaca",       20.5, -30.5),
    ("S. Africa Saldanha",   18.35, -33.0),
    ("S. Africa Richards",   27.6, -26.5),
    ("S. Africa Newcastle",  30.3, -27.8),
    ("S. Africa East London",29.9, -33.0),
    ("S. Africa Secunda",    28.0, -27.9),
    ("S. Africa Coega",      30.2, -31.0),
    ("Kenya Lamu",           40.9, -2.0),
    ("Somalia Mogadishu",    45.3,  2.0),
    ("Madagascar Toamasina", 49.4, -18.1),
    ("Madagascar Mahajanga", 43.7, -15.7),
    ("Ethiopia Adama",       38.8, 9.0),
    ("Tanzania Zanzibar",    39.2, -6.2),
    ("Tanzania Tanga",       39.1, -5.1),
    ("Uganda Port",          31.2, 0.5),
]


def haversine(lon1, lat1, lon2, lat2):
    """Great-circle distance in km."""
    R = 6371.0
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2 * R * math.asin(min(1.0, math.sqrt(a)))


def nearest_dist(lon, lat, points):
    """Minimum great-circle distance in km from (lon, lat) to any point.

    `points` may contain 2-tuples (lon, lat) or 3-tuples (name, lon, lat).
    """
    def _one(pt):
        if isinstance(pt, (list, tuple)):
            if len(pt) == 3 and isinstance(pt[0], str):
                return pt[1], pt[2]
        return pt[0], pt[1]
    return min(haversine(lon, lat, * _one(p)) for p in points)


# ------------------------------------------------------------------
# Region classifier (based on lon/lat boxes) -- reproduces Africa's
# well-known renewable-resource patterns without external data.
# ------------------------------------------------------------------
def resource_profile(lon: float, lat: float):
    """Return (theo_pv, theo_wind) for a coordinate inside Africa."""
    # Sahara (Saharan interior, 15N-30N, -15E to 35E)
    if 12 <= lat <= 30 and -15 <= lon <= 30:
        # Sahel-edge (12-18N): very high PV
        pv = np.random.uniform(0.82, 0.92)
        wind = np.random.uniform(0.45, 0.65)
        return pv, wind
    # Mediterranean coast (30-36N, -10E to 35E)
    if 30 <= lat <= 36 and -12 <= lon <= 35:
        return np.random.uniform(0.75, 0.85), np.random.uniform(0.55, 0.70)
    # Southern Sahara / Namib (15-30S, -20E to 20E)
    if -30 <= lat <= -15 and -20 <= lon <= 20:
        return np.random.uniform(0.78, 0.85), np.random.uniform(0.55, 0.72)
    # Namib coast (very windy Atlantic, -20-30S, 12-15E)
    if -30 <= lat <= -18 and 12 <= lon <= 15:
        return np.random.uniform(0.75, 0.82), np.random.uniform(0.72, 0.85)
    # South African plateau
    if -32 <= lat <= -22 and 15 <= lon <= 33:
        return np.random.uniform(0.72, 0.82), np.random.uniform(0.45, 0.65)
    # Horn of Africa / Somalia coast
    if -2 <= lat <= 12 and 40 <= lon <= 52:
        return np.random.uniform(0.75, 0.82), np.random.uniform(0.55, 0.75)
    # East African highlands (Ethiopia, Kenya)
    if 3 <= lat <= 16 and 32 <= lon <= 42:
        return np.random.uniform(0.78, 0.85), np.random.uniform(0.40, 0.55)
    # Lake region (East African lakes)
    if -4 <= lat <= 4 and 28 <= lon <= 36:
        return np.random.uniform(0.68, 0.78), np.random.uniform(0.35, 0.50)
    # Madagascar
    if -26 <= lat <= -12 and 43 <= lon <= 51:
        return np.random.uniform(0.70, 0.78), np.random.uniform(0.40, 0.55)
    # West African coast (Sahel / Saharan)
    if 4 <= lat <= 22 and -18 <= lon <= 12:
        pv = 0.80 if lat > 10 else 0.70
        return pv + np.random.uniform(-0.03, 0.03), np.random.uniform(0.35, 0.55)
    # Central Africa (Congo basin, equatorial)
    if -5 <= lat <= 5 and 8 <= lon <= 32:
        return np.random.uniform(0.55, 0.65), np.random.uniform(0.28, 0.42)
    # Default (inland / unclassified)
    return np.random.uniform(0.62, 0.75), np.random.uniform(0.35, 0.55)


def generate_africa_grid(
    lon_min: float = -18,
    lon_max: float = 52,
    lat_min: float = -35,
    lat_max: float = 37,
    step: float  = 2.0,
    seed: int    = 42,
) -> list[dict]:
    """Return a list of grid-cell dicts with the six feature columns."""
    rng = np.random.default_rng(seed)
    cells = []
    lon = lon_min
    while lon <= lon_max:
        lat = lat_min
        while lat <= lat_max:
            pv, wind = resource_profile(float(lon), float(lat))
            cells.append({
                "lon": float(lon),
                "lat": float(lat),
                "theo_pv":  round(float(pv), 4),
                "theo_wind": round(float(wind), 4),
                "grid_dist_km":  round(nearest_dist(float(lon), float(lat), GRID_CITIES), 1),
                "road_dist_km":  round(nearest_dist(float(lon), float(lat), ROAD_HUBS),   1),
                "ocean_dist_km": round(nearest_dist(float(lon), float(lat), PORTS),      1),
                "waterbody_dist_km": round(nearest_dist(float(lon), float(lat), _WATER), 1),
            })
            lat += step
        lon += step
    return cells


# Inland water bodies (major lakes & rivers) as distance reference.
_WATER = [
    (29.7, -4.5),   # Lake Victoria
    (22.7, -13.0),  # Lake Tanganyika
    (29.3, -9.4),   # Lake Malawi
    (24.0,  -5.5),  # Lake Turkana
    (23.7, -12.0),  # Lake Edward
    (20.5, -23.6),  # Lake Ngami
    (22.0, -25.0),  # Lake Bangweulu
    (17.5, -28.2),  # Okavango
    (27.0, -20.5),  # Senegal river basin
    (10.0,  30.0),  # Nile corridor
    (35.0,  -0.5),  # Inland West Africa rivers
    (15.0,  15.0),  # Chad basin
    (32.0,   9.0),  # Nile / Blue Nile
    (31.0,  30.0),  # N. Egypt water sources
    (16.0, -19.0),  # Orange river
]


if __name__ == "__main__":
    cells = generate_africa_grid()
    print(f"Generated {len(cells)} grid cells")
    print("First 3:", cells[:3])
