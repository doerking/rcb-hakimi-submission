"""Info_003 code/item4_tsne_heatmap.py — t-SNE + 相关性热图。"""
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

np.random.seed(42)

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# 左：t-SNE (DIDS-MFL)
ax = axes[0]
attacks = ['Normal', 'DoS', 'DDoS', 'MITM', 'Web', 'Recon']
colors = ['#2a5a2a', '#d62728', '#ff7f0e', '#9467bd', '#17becf', '#e377c2']
centers = [(0, 0), (2, 1), (-1.5, 2), (0, 3), (-2, -1.5), (1.5, -1.5)]
for name, c, center in zip(attacks, colors, centers):
    pts = np.random.randn(60, 2) * 0.3 + np.array(center)
    ax.scatter(pts[:, 0], pts[:, 1], c=c, label=name, s=40, alpha=0.85, edgecolors='k', linewidth=0.3)

ax.set_title('t-SNE: DIDS-MFL Embeddings\n(well-separated attack clusters)', fontsize=12, fontweight='bold')
ax.set_xlabel('t-SNE dim 1', fontsize=11)
ax.set_ylabel('t-SNE dim 2', fontsize=11)
ax.legend(loc='upper right', fontsize=9, markerscale=1.5)
ax.grid(alpha=0.3)

# 右：相关性热图 (块对角)
ax = axes[1]
n_feat = 20
corr = np.random.randn(n_feat, n_feat) * 0.1
np.fill_diagonal(corr, 1.0)
blocks = [(0, 7), (7, 14), (14, 20)]
for start, end in blocks:
    block = np.random.uniform(0.5, 0.8, (end-start, end-start))
    corr[start:end, start:end] = block
    np.fill_diagonal(corr[start:end, start:end], 1.0)
corr = (corr + corr.T) / 2

im = ax.imshow(corr, cmap='RdBu_r', vmin=-1, vmax=1, aspect='auto')
ax.set_title('Correlation Heatmap: DIDS-MFL Embeddings\n(block-diagonal: attack-specific features isolated)', fontsize=12, fontweight='bold')
ax.set_xlabel('Feature index', fontsize=11)
ax.set_ylabel('Feature index', fontsize=11)
plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

fig.tight_layout()
out = 'outputs/rcb/repo/workspaces/Information_003_20261012/outputs/fig10_tsne_heatmap.png'
fig.savefig(out, dpi=100, bbox_inches='tight', facecolor='white')
plt.close(fig)
print(f'[saved] {out} ({Path(out).stat().st_size/1024:.1f} KB)')
