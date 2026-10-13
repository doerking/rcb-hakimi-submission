"""Item 3 · 层级自洽验证（BN001-010 求和 == CN01）"""
import pandas as pd, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent / "data" / "HEEW_Mini-Dataset"
OUT = Path(__file__).resolve().parent.parent / "report" / "images"
OUT.mkdir(parents=True, exist_ok=True)
EL = "Electricity [kW]"
bns = [f"BN{i:03d}_energy.csv" for i in range(1, 11)]
dfs = [pd.read_csv(BASE / b) for b in bns]
s10 = sum(d[EL] for d in dfs)
cn = pd.read_csv(BASE / "CN01_energy.csv")
tot = pd.read_csv(BASE / "Total_energy.csv")

print("=== Item3 层级自洽 ===")
print("BN 数:", len(bns), "| 行数:", len(cn))
d_cn = (s10 - cn[EL]).abs()
print(f"sum10 vs CN01: max_abs={d_cn.max():.3e}  mean_abs={d_cn.mean():.3e}")
d_tot = (s10 - tot[EL]).abs()
print(f"sum10 vs Total: max_abs={d_tot.max():.3e}  mean_abs={d_tot.mean():.3e}")
rel = (d_cn / cn[EL].abs().clip(lower=1e-9))
print(f"mean_rel={rel.mean():.3e}")

# 反推: 如果有第 11 个节点
d_cn01 = pd.read_csv(BASE / "CN01_energy.csv")

# 2014-01-01 曲线（对齐目标图 target_study/images/hierarchical_check.png · 标题日期 = 2014-01-01）
m = (cn["year"] == 2014) & (cn["month"] == 1) & (cn["day"] == 1)
h = cn.loc[m, "hour"].values
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.plot(h, cn.loc[m, EL].values, "o-", color="tab:blue", lw=2, ms=4, label="Community Record")
ax.plot(h, s10[m].values, "s--", color="tab:orange", lw=2, ms=4, label="Sum of Buildings")
ax.set_xlabel("Hour of Day"); ax.set_ylabel("Electricity [kW]")
ax.set_title("CN01 Aggregation Check on 2014-01-01")
ax.set_xticks(range(0, 24, 5))
ax.legend(); ax.grid(alpha=.3)
fig.tight_layout(); fig.savefig(OUT / "hierarchical_check.png", dpi=120)
print("saved report/images/hierarchical_check.png")

# 各节点占比（顺带）
print("\n=== 各 BN 占比（均值）===")
tot_mean = s10.mean()
for b, d in zip(bns, dfs):
    print(f"  {b}: {d[EL].mean()/tot_mean*100:5.2f}%")
