"""Life_003 code/item2_performance.py — Alignment time & file size bar chart."""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

df = pd.read_csv('outputs/rcb/repo/workspaces/Life_003_20261012/performance_summary.csv')
print(df)

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# 左：Alignment Time
ax = axes[0]
tools = ['Uncalled4', 'f5c', 'Nanopolish', 'Tombo']
chemistries = df['Chemistry'].unique()
colors = ['#4a90c5', '#ff7f0e', '#5fa060', '#d62728']
x = np.arange(len(tools))
width = 0.2
for i, chem in enumerate(chemistries):
    subset = df[df['Chemistry'] == chem].set_index('Tool')
    vals = [subset.loc[t, 'Time_min'] if t in subset.index else 0 for t in tools]
    ax.bar(x + i*width, vals, width, label=chem, color=colors[i], edgecolor='k', linewidth=0.3)
ax.set_xticks(x + width*1.5)
ax.set_xticklabels(tools, rotation=45, ha='right')
ax.set_ylabel('Time (minutes)', fontsize=11)
ax.set_title('Alignment Time', fontsize=12, fontweight='bold')
ax.legend(fontsize=9)
ax.grid(axis='y', alpha=0.3)

# 右：File Size (log scale)
ax = axes[1]
for i, chem in enumerate(chemistries):
    subset = df[df['Chemistry'] == chem].set_index('Tool')
    vals = [max(subset.loc[t, 'FileSize_MB'], 1) if t in subset.index else 1 for t in tools]
    ax.bar(x + i*width, vals, width, label=chem, color=colors[i], edgecolor='k', linewidth=0.3)
ax.set_xticks(x + width*1.5)
ax.set_xticklabels(tools, rotation=45, ha='right')
ax.set_ylabel('File Size (MB)', fontsize=11)
ax.set_title('Output File Size', fontsize=12, fontweight='bold')
ax.legend(fontsize=9)
ax.set_yscale('log')
ax.grid(axis='y', alpha=0.3)

fig.suptitle('Table 1: Performance Comparison', fontsize=13, fontweight='bold', y=1.02)
fig.tight_layout()
out = 'outputs/rcb/repo/workspaces/Life_003_20261012/outputs/table1_performance.png'
fig.savefig(out, dpi=100, bbox_inches='tight', facecolor='white')
plt.close(fig)
print(f'[saved] {out} ({Path(out).stat().st_size/1024:.1f} KB)')
