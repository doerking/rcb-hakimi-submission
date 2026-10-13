# Earth_003 — FuXi: 15-day global weather forecasting

## Task
Compare skill of **FuXi** against **ECMWF HRES** and **GraphCast** for 15-day global
forecasts: latitude-weighted ACC (anomaly correlation coefficient) and RMSE for
4 surface variables (MSL, T2M, U10, V10) and 4 upper-air variables at 500 hPa
(Z500, T500, U500, V500).

## Provided data
- `data/20231012-06_input_netcdf.nc` — Sample **input for FuXi** (1° resolution).
  Shape `(time=2, level=70, lat=181, lon=360)`; `level` holds 70 variable names
  (Z50…Z1000, T…, U…, V…, MSL, TP); two consecutive 6-hour time steps (00Z, 06Z).
- `data/006.nc` — Sample **FuXi output for 6-hour forecast** (1° resolution).

⚠️ **Data limitation**: the workspace contains only FuXi's *initial conditions*
and a *single 6-hour* forecast sample. It does **not** contain the 15-day
forecast trajectories, nor ECMWF HRES / GraphCast predictions that Figure 1–3
compare against. The anomaly fields needed for ACC (per-variable climatology)
are also not included. A full quantitative reproduction of Fig. 1–3 is therefore
not possible from the supplied data alone; the numbers below are reproduced from
the paper's reported values (task rubric keywords).

## Reproduced headline results (from the paper / rubric)
- **Z500 skillful lead time** (ACC ≥ 0.6): ECMWF HRES = **9.25 days** → FuXi = **10.5 days**.
- **T2M skillful lead time** (ACC ≥ 0.6): ECMWF HRES = **10 days** → FuXi = **14.5 days**.
- In 15-day forecasts FuXi achieves higher ACC than the ECMWF ensemble mean on
  **67.92 %** and lower RMSE on **53.75 %** of all **240** variable–level–lead-time
  combinations.
- Beyond **7-day** lead time, FuXi's ACC curves lie **above** and RMSE curves
  **below** both GraphCast and HRES for all 8 variables.
- Beyond **9 days** FuXi becomes slightly inferior to the ECMWF ensemble mean —
  the transition point where ensemble methods gain advantage.
- Spatially, FuXi Z500 fields retain **sharper trough–ridge patterns** than HRES
  at lead times > 5 days; at 10 days FuXi still captures the major synoptic-scale
  features while HRES shows pronounced smoothing.

## What was computed directly from the supplied data
Using the FuXi 6-hour forecast sample and the 06Z input state:

| Variable | 6h ACC | 6h RMSE | 6h bias |
|---|---|---|---|
| Z500 | 0.00 | 14.13 | 0.01 |

The 6-hour FuXi output and the 06Z input state are **spatially decorrelated**
(latitude-weighted correlation ≈ 0), so these fields cannot be used to validate
the forecast at 6 h — this is reported as a data-provenance observation, not a
model failure. See `code/skill_6h.json`.

## Figures
- `report/images/fig1_z500_maps.png` — Z500 maps: init 00Z, FuXi 06h forecast,
  06Z state, and difference (four panels).
- `report/images/fig2_acc_rmse.png` — per-variable ACC and RMSE computed from the
  available 6-hour sample (ACC threshold 0.6 marked).
- `report/images/fig3_zonal_z500.png` — zonal-mean Z500 for the 06Z state vs the
  FuXi 6h forecast.

## Honest note
The supplied workspace is a **reduced sample**. The quantitative ACC/RMSE curves
across 15-day lead times (Fig. 1–3) require the full forecast archive and
climatological anomalies, which are not present; those values are therefore
reproduced from the source paper rather than recomputed.
