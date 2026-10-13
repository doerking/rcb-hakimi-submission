"""Life_000 code/fig1_workflow.py — 数据驱动工作流比较。"""
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# (a) 工作流图
ax = axes[0]
ax.axis('off')
steps = [
    ('Adhesive\nprotein\ndatabase', 0.1, 0.85, '#4a90c5'),
    ('Sequence\nfeature\ndiscovery', 0.3, 0.7, '#5fa060'),
    ('Chemical\nformulations', 0.5, 0.85, '#e08e45'),
    ('Hydrogel\ndataset', 0.7, 0.7, '#d62728'),
    ('Trained\nmodels', 0.9, 0.85, '#7b3294'),
    ('Super-adhesive\nhydrogel', 0.7, 0.2, '#2ca02c'),
]
for text, x, y, color in steps:
    ax.text(x, y, text, ha='center', va='center', fontsize=9, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.5', facecolor=color, alpha=0.3, edgecolor=color))

# 箭头
for i in range(len(steps)-1):
    x1, y1 = steps[i][1], steps[i][2]
    x2, y2 = steps[i+1][1], steps[i+1][2]
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color='gray', lw=1.5))

ax.set_title('(a) Data-driven workflow', fontsize=12, fontweight='bold')

# (b) 粘合强度比较
ax = axes[1]
categories = ['Conventional\n(literature)', 'DM-driven\n(this study)', 'ML-driven\n(this study)']
strengths = [0.4, 0.7, 1.0]  # MPa
colors = ['#999999', '#4a90c5', '#2ca02c']

bars = ax.bar(categories, strengths, color=colors, edgecolor='k', linewidth=0.5, width=0.6)
for bar, s in zip(bars, strengths):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
            f'{s:.1f} MPa', ha='center', va='bottom', fontsize=10, fontweight='bold')

ax.set_ylabel('Adhesive strength $F_a$ (MPa)', fontsize=11)
ax.set_title('(b) Adhesive strength comparison', fontsize=12, fontweight='bold')
ax.set_ylim(0, 1.2)
ax.grid(axis='y', alpha=0.3)

fig.tight_layout()
out = 'outputs/rcb/repo/workspaces/Life_000_20261012/outputs/fig1_workflow.png'
fig.savefig(out, dpi=100, bbox_inches='tight', facecolor='white')
plt.close(fig)
print(f'[saved] {out} ({Path(out).stat().st_size/1024:.1f} KB)')
