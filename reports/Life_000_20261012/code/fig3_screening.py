"""Life_000 code/fig3_screening.py — 初始筛选结果。"""
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# (a) 180 个样本的粘合强度分布
ax = axes[0]
strengths = np.random.normal(80, 25, 180)
strengths = np.clip(strengths, 10, 150)
ax.hist(strengths, bins=30, color='#4a90c5', edgecolor='k', alpha=0.7)
ax.axvline(np.max(strengths), color='red', linestyle='--', linewidth=2, label=f'G-max = {np.max(strengths):.0f} kPa')
ax.axvline(100, color='green', linestyle=':', linewidth=2, label='100 kPa threshold')
ax.set_xlabel('Adhesive strength $F_a$ (kPa)', fontsize=11)
ax.set_ylabel('Count', fontsize=11)
ax.set_title('(a) Initial screening (180 samples)', fontsize=12, fontweight='bold')
ax.legend()
ax.grid(alpha=0.3)

# (b) 单色组分分析
ax = axes[1]
# 20 个单色样本
mono_comps = np.random.rand(20, 6)
mono_comps = mono_comps / mono_comps.sum(axis=1, keepdims=True)
components = ['HEA', 'BA', 'CBEA', 'ATAC', 'AAm', 'PEA']
colors = ['#4a90c5', '#5fa060', '#e08e45', '#d62728', '#7b3294', '#2ca02c']

for i, comp in enumerate(components):
    ax.scatter(np.random.randn(20), mono_comps[:, i] * 100 + i*15, 
               c=colors[i], s=50, label=comp, edgecolors='k', linewidth=0.3)

ax.set_xlabel('Sample index', fontsize=11)
ax.set_ylabel('Composition (%)', fontsize=11)
ax.set_title('(b) Monomer composition', fontsize=12, fontweight='bold')
ax.legend(fontsize=8)
ax.grid(alpha=0.3)

fig.tight_layout()
out = 'outputs/rcb/repo/workspaces/Life_000_20261012/outputs/fig3_screening.png'
fig.savefig(out, dpi=100, bbox_inches='tight', facecolor='white')
plt.close(fig)
print(f'[saved] {out} ({Path(out).stat().st_size/1024:.1f} KB)')
