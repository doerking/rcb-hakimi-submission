"""Item 2 · 相关热图（对齐目标图 target_study/images/corr_elec_weather.png）

目标图 = 7×7 自相关矩阵：
  变量序 = [Electricity, Temperature, Dew Point, Humidity, Wind Speed, Pressure, Precipitation]
  目标值（读图）：Elec-Temp=-0.57 · Temp-DewPoint=0.97 · DewPoint-Humidity=0.38 · Wind-Pressure=-0.40 …
  标题 = "Correlation: Electricity & Weather"
数据 = Total_energy.csv + Total_weather.csv（2014 全年）· merged on (year,month,day,hour)
"""
import pandas as pd, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent / "data" / "HEEW_Mini-Dataset"
OUT = Path(__file__).resolve().parent.parent / "report" / "images"
OUT.mkdir(parents=True, exist_ok=True)
en = pd.read_csv(BASE / "Total_energy.csv")
wx = pd.read_csv(BASE / "Total_weather.csv")

wx["dt"] = pd.to_datetime(wx["datetime"])
for k in ("year", "month", "day", "hour"):
    wx[k] = getattr(wx["dt"].dt, k)
df = en.merge(wx.drop(columns=["datetime", "dt"]), on=["year", "month", "day", "hour"], how="inner")
print("merged:", df.shape)

VARS = ["Electricity [kW]", "Temperature [°F]", "Dew Point [°F]", "Humidity [%]",
        "Wind Speed [mph]", "Pressure [in]", "Precipitation [in]"]
SHORT = [v.split(" [")[0] for v in VARS]
M = df[VARS].corr(method="pearson")
M.index = SHORT; M.columns = SHORT
print("\n=== 7×7 相关矩阵 ===")
print(M.round(3).to_string())

# 对齐目标图关键值核对
print("\n=== 对照目标图 ===")
for a, b, tv in [("Electricity", "Temperature", -0.57), ("Electricity", "Dew Point", -0.56),
                 ("Temperature", "Dew Point", 0.97), ("Dew Point", "Humidity", 0.38),
                 ("Wind Speed", "Pressure", -0.40)]:
    print(f"  {a:12s}–{b:12s} 目标={tv:+.2f}  实测={M.loc[a, b]:+.3f}")

fig, ax = plt.subplots(figsize=(7, 6))
im = ax.imshow(M.values.astype(float), cmap="RdBu_r", vmin=-1, vmax=1)
ax.set_xticks(range(len(VARS))); ax.set_xticklabels(SHORT, rotation=45, ha="right")
ax.set_yticks(range(len(VARS))); ax.set_yticklabels(SHORT)
for i in range(len(VARS)):
    for j in range(len(VARS)):
        v = M.values[i, j]
        ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=7,
                color="white" if abs(v) > .6 else "black")
ax.set_title("Correlation: Electricity & Weather")
fig.colorbar(im, ax=ax, shrink=.85)
fig.tight_layout(); fig.savefig(OUT / "corr_elec_weather.png", dpi=120)
print("\nsaved report/images/corr_elec_weather.png")
