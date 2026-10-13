"""Info_003 code/item2_framework.py — DIDS-MFL 框架示意图。"""
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path

fig, ax = plt.subplots(figsize=(12, 7))
ax.set_xlim(0, 12); ax.set_ylim(0, 8); ax.axis('off')
fig.patch.set_facecolor('white')

# 顶部输入
ax.add_patch(patches.Rectangle((4.5, 6.8), 3, 0.7, facecolor='#3d5a80', edgecolor='k', linewidth=1.5))
ax.text(6, 7.15, 'Traffic Features\n(e.g. NF-UNSW-NB15-v2)', ha='center', va='center',
        fontsize=11, color='white', fontweight='bold')

# 三条分支
modules = [
    (0.5, 4.5, '① Statistical\nDisentanglement\n(SD)',
     'Non-parametric MI minimization\nEnforces order-preserving\nconstraints\n\n→ Distinguishable feature\ndistributions',
     '#4a90c5'),
    (4.5, 4.5, '② Representational\nDisentanglement\n(RD)',
     'Orthogonal regularization\n(Low-correlation node embeddings)\nAttack-specific dimensions\n\n→ Well-separated embeddings',
     '#e08e45'),
    (8.5, 4.5, '③ Multi-layer Graph\nDiffusion\n(MLGRAND)',
     'PM-inspired nonlinear diffusion\nSpatial-temporal coefficients SS\nFuses topology + time\n\n→ Dynamic aggregation',
     '#5fa060'),
]

for x0, y0, title, desc, color in modules:
    ax.add_patch(patches.FancyBboxPatch((x0, y0-1), 3, 2.5,
                                         boxstyle="round,pad=0.15,rounding_size=0.1",
                                         facecolor=color, edgecolor='k', linewidth=1.5, alpha=0.9))
    ax.text(x0+1.5, y0+1.4, title, ha='center', va='center',
            fontsize=11, color='white', fontweight='bold')
    ax.text(x0+1.5, y0+0.5, desc, ha='center', va='center',
            fontsize=8, color='white')

# 汇聚箭头
for x0 in [2, 6, 10]:
    ax.annotate('', xy=(6, 3.5), xytext=(x0, 4.4),
                arrowprops=dict(arrowstyle='->', color='k', linewidth=2))

# 底部融合
ax.add_patch(patches.Rectangle((4, 2.6), 4, 0.9, facecolor='#3d5a80', edgecolor='k', linewidth=1.5))
ax.text(6, 3.05, 'Dynamic Attack-Specific\nRepresentation Fusion', ha='center', va='center',
        fontsize=11, color='white', fontweight='bold')

# 输出
ax.annotate('', xy=(6, 1.9), xytext=(6, 2.5),
            arrowprops=dict(arrowstyle='->', color='k', linewidth=2))

ax.add_patch(patches.Rectangle((3.5, 0.5), 5, 1.2, facecolor='#2a4a2a', edgecolor='k', linewidth=1.5))
ax.text(6, 1.1, '⚡  Detection: Known + Unknown + Few-Shot\nF1 96.00%  ·  NMI 92.04%  (NF-UNSW-NB15-v2)', ha='center', va='center',
        fontsize=11, color='white', fontweight='bold')

ax.set_title('DIDS-MFL Framework: Disentangled Dynamic Intrusion Detection', fontsize=14, fontweight='bold', pad=15)

out = 'outputs/rcb/repo/workspaces/Information_003_20261012/outputs/fig7_framework.png'
fig.savefig(out, dpi=100, bbox_inches='tight', facecolor='white')
plt.close(fig)
print(f'[saved] {out} ({Path(out).stat().st_size/1024:.1f} KB)')
