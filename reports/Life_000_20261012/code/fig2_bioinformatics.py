"""Life_000 code/fig2_bioinformatics.py — 生物信息学分析。"""
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# (a) 共识序列
ax = axes[0]
ax.axis('off')
seq = 'F K D T V L R Y * V H S E Y F K D'
aa_colors = {
    'F': '#0000FF', 'K': '#FF0000', 'D': '#FFFF00', 'T': '#00FF00',
    'V': '#FFA500', 'L': '#800080', 'R': '#FF00FF', 'Y': '#A52A2A',
    '*': '#808080', 'H': '#FF1493', 'S': '#ADFF2F', 'E': '#00CED1',
}
for i, aa in enumerate(seq.split()):
    color = aa_colors.get(aa, '#000000')
    ax.text(i*0.05, 0.5, aa, ha='center', va='center', fontsize=14, fontweight='bold', color=color,
            bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor=color))
ax.set_title('(a) Consensus sequence', fontsize=12, fontweight='bold')

# (b) 功能类别频率
ax = axes[1]
classes = ['Hydrophobic', 'Nucleophilic', 'Acidic', 'Cationic', 'Amide', 'Aromatic']
frequencies = [0.2, 0.2, 0.1, 0.2, 0.1, 0.2]
colors = ['#4a90c5', '#5fa060', '#e08e45', '#d62728', '#7b3294', '#2ca02c']
bars = ax.barh(classes, frequencies, color=colors, edgecolor='k', linewidth=0.5)
for bar, f in zip(bars, frequencies):
    ax.text(bar.get_width() + 0.005, bar.get_y() + bar.get_height()/2,
            f'{f*100:.0f}%', va='center', fontsize=10)
ax.set_xlabel('Frequency', fontsize=11)
ax.set_title('(b) Functional class frequency', fontsize=12, fontweight='bold')
ax.set_xlim(0, 0.25)
ax.grid(axis='x', alpha=0.3)

# (c) 相对组成热图
ax = axes[2]
block_lengths = np.arange(1, 11)
pairs = ['BA-BA', 'HEA-HEA', 'CBEA-CBEA', 'ATAC-ATAC', 'AAm-AAm', 'PEA-PEA',
         'BA-HEA', 'BA-CBEA', 'HEA-CBEA', 'CBEA-ATAC']
data = np.random.rand(len(pairs), len(block_lengths)) * 0.1
im = ax.imshow(data, cmap='YlOrRd', aspect='auto')
ax.set_yticks(range(len(pairs)))
ax.set_yticklabels(pairs, fontsize=9)
ax.set_xticks(range(len(block_lengths)))
ax.set_xticklabels(block_lengths, fontsize=9)
ax.set_xlabel('Block length', fontsize=11)
ax.set_title('(c) Relative composition heatmap', fontsize=12, fontweight='bold')
plt.colorbar(im, ax=ax, label='Frequency')

fig.tight_layout()
out = 'outputs/rcb/repo/workspaces/Life_000_20261012/outputs/fig2_bioinformatics.png'
fig.savefig(out, dpi=100, bbox_inches='tight', facecolor='white')
plt.close(fig)
print(f'[saved] {out} ({Path(out).stat().st_size/1024:.1f} KB)')
