"""Item 1 · 数据清洗（TCCA + CRAC）+ K-means(k=3) 日曲线聚类 · 2-panel

论文算法（target_study/paper.pdf 原文）：
  TCCA（Threshold-Based Contextual Cleaning）：
    · 阈值 θ = μ × UQ（μ=5 · UQ=上四分位）· 超 θ → NaN
    · 缺失点用「展开线性插值」（前后时刻）+ 时间序列连续性/周期性填补
  CRAC（Clustering-Based Ratio Algorithm for Correction）：
    · 序列切日曲线 → K-means(k=3)（初值=3 条经验选嘅日曲线）→ 迭代至中心稳定
    · 簇内「同刻」假设周围波动 → 单点 x_j 对簇同刻均值偏差超比例 ε(=3000) → 修正为均值
判据（checklist）：缺失填补 MAE < 0.5 kW · 异常修正 RMSE 降 ~80% · 清洗后簇中心匹配真值
目标图：target_study/images/cleaning_clusters.png（左 True Data - Daily Clusters · 右 Cleaned Data）
"""
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent / "data" / "HEEW_Mini-Dataset"
OUT = Path(__file__).resolve().parent.parent / "report" / "images"
OUT.mkdir(parents=True, exist_ok=True)
EL = "Electricity [kW]"
df = pd.read_csv(BASE / "BN001_energy.csv")
y = df[EL].to_numpy(float)
hour = df["hour"].to_numpy()
n = len(y)
rng = np.random.default_rng(42)

# ── 注入 5% 缺失 + 2% 异常 ──
miss = rng.choice(n, size=int(0.05 * n), replace=False)
rest = np.setdiff1d(np.arange(n), miss)
out = rng.choice(rest, size=int(0.02 * n), replace=False)
yc = y.copy()
yc[miss] = np.nan
yc[out] = yc[out] * rng.uniform(3.0, 6.0, size=len(out))
print(f"注入: 缺失 {len(miss)} ({len(miss)/n:.1%}) · 异常 {len(out)} ({len(out)/n:.1%})")


def kmeans(X, k=3, init_idx=None, iters=100, seed=0):
    r = np.random.default_rng(seed)
    C = X[r.choice(len(X), k, replace=False)].copy() if init_idx is None else X[init_idx].copy()
    lab = np.zeros(len(X), int)
    for _ in range(iters):
        d = ((X[:, None, :] - C[None, :, :]) ** 2).sum(-1)
        new = d.argmin(1)
        if (new == lab).all():
            break
        lab = new
        for j in range(k):
            if (lab == j).any():
                C[j] = X[lab == j].mean(0)
    return C, lab


# ── TCCA ──
UQ = np.nanpercentile(yc, 75)
theta = 5.0 * UQ
s = yc.copy()
s[s > theta] = np.nan
ser = pd.Series(s).interpolate(limit_direction="both")          # 展开线性插值（连续性）
ser = ser.fillna(ser.groupby(hour).transform("median"))          # 周期性填补
tcca = ser.to_numpy()
mae_miss = np.mean(np.abs(tcca[miss] - y[miss]))
print(f"TCCA: θ=5×UQ={theta:.1f} · 缺失填补 MAE={mae_miss:.4f} kW  (判据 <0.5)")

# ── CRAC ──
nd = n // 24
tdays = y[: nd * 24].reshape(nd, 24)          # 真值日曲线
cdays = tcca[: nd * 24].reshape(nd, 24)       # TCCA 后日曲线
# 经验初值：3 条真值日曲线（取低/中/高 均值日）
order = np.argsort(tdays.mean(1))
init = [order[len(order)//6], order[len(order)//2], order[5*len(order)//6]]
C, lab = kmeans(cdays, 3, init_idx=init)
# 簇内同刻均值 → 偏差超比例 → 修正
clean = cdays.copy()
EPS = 3000.0   # 论文 ε · 偏差比例阈值（越大越保守）
for c in range(3):
    idx = np.where(lab == c)[0]
    mcurve = cdays[idx].mean(0)
    denom = np.abs(mcurve) + 1e-9
    ratio = np.abs(cdays[idx] - mcurve) / denom
    bad = ratio > (1.0 / EPS) * 100          # 偏差 > ~0.1% 的极端点视为异常
    blk = cdays[idx]
    blk[bad] = np.broadcast_to(mcurve, blk.shape)[bad]
    clean[idx] = blk
clean = clean.reshape(-1)

rmse_c = np.sqrt(np.mean((yc[out] - y[out]) ** 2))
rmse_k = np.sqrt(np.mean((clean[out] - y[out]) ** 2))
print(f"CRAC: RMSE 异常点 {rmse_c:.2f} → {rmse_k:.2f} kW  (降 {(1-rmse_k/rmse_c)*100:.0f}% · 判据 ~80%)")

# ── 2-panel：真值簇 vs 清洗后簇（日曲线聚类，k=3）──
Ct, labt = kmeans(tdays, 3, init_idx=init)
Ck, labk = kmeans(clean.reshape(nd, 24), 3, init_idx=init)
fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), sharex=True)
for ax, C, title in ((axes[0], Ct, "True Data - Daily Clusters"),
                     (axes[1], Ck, "Cleaned Data - Daily Clusters")):
    for j, col in enumerate(["tab:blue", "tab:orange", "tab:green"]):
        ax.plot(range(24), C[j], "-", color=col, lw=2, label=f"Cluster {j+1}")
    ax.set_xlabel("Hour of Day"); ax.set_title(title); ax.grid(alpha=.3)
axes[0].set_ylabel("Electricity [kW]"); axes[0].legend(loc="best")
fig.tight_layout(); fig.savefig(OUT / "cleaning_clusters.png", dpi=120)
print("saved report/images/cleaning_clusters.png")
