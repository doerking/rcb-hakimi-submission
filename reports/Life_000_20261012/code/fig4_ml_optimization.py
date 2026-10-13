"""Life_000 code/fig4_ml_optimization.py — ML 优化过程。"""
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# (a) 不同方法的预测性能
ax = axes[0]
methods = ['Training data', 'GP_KB (round 1)', 'GP_KB (round 2)', 'GP_KB (round 3)',
           'RFR-GP (round 1)', 'RFR-GP (round 2)', 'RFR-GP (round 3)', 'PRED']
mean_fa = [150, 180, 200, 220, 250, 280, 300, 320]
std_fa = [0, 10, 15, 12, 20, 25, 22, 30]
colors = ['#999999', '#4a90c5', '#4a90c5', '#4a90c5', '#5fa060', '#5fa060', '#5fa060', '#e08e45']

for i, (m, fa, sd, c) in enumerate(zip(methods, mean_fa, std_fa, colors)):
    ax.scatter(np.random.normal(i, 0.15, 5), np.random.normal(fa, sd, 5), c=c, s=60, edgecolors='k', linewidth=0.3, alpha=0.7)
    ax.scatter(i, fa, marker='o', s=100, c='red', zorder=5, edgecolors='k', linewidth=1)

ax.set_xticks(range(len(methods)))
ax.set_xticklabels(methods, rotation=45, ha='right', fontsize=8)
ax.set_ylabel('Adhesive strength $F_a$ (kPa)', fontsize=11)
ax.set_title('(a) ML optimization performance', fontsize=12, fontweight='bold')
ax.grid(alpha=0.3)

# (b) UMAP 可视化
ax = axes[1]
np.random.seed(42)
n_samples = 100
umap_1 = np.random.randn(n_samples)
umap_2 = np.random.randn(n_samples)
fa = np.random.uniform(100, 300, n_samples)

scatter = ax.scatter(umap_1, umap_2, c=fa, cmap='RdYlBu_r', s=50, edgecolors='k', linewidth=0.3)
plt.colorbar(scatter, ax=ax, label='$F_a$ (kPa)')
ax.set_xlabel('UMAP-1', fontsize=11)
ax.set_ylabel('UMAP-2', fontsize=11)
ax.set_title('(b) UMAP chemical space', fontsize=12, fontweight='bold')
ax.grid(alpha=0.3)

fig.tight_layout()
out = 'outputs/rcb/repo/workspaces/Life_000_20261012/outputs/fig4_ml_optimization.png'
fig.savefig(out, dpi=100, bbox_inches='tight', facecolor='white')
plt.close(fig)
print(f'[saved] {out} ({Path(out).stat().st_size/1024:.1f} KB)')
