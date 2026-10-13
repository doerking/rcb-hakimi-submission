"""Info_003 code/item1_f1_gap.py — E-GraphSAGE F1 分数在不同攻击类型的巨大波动。"""
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

attacks = ['MITM', 'DDoS', 'DoS', 'PortScan', 'WebAttack', 'BruteForce', 'Recon', 'Spoof']
f1_egr = [18, 93, 88, 55, 72, 40, 68, 60]  # E-GraphSAGE

fig, ax = plt.subplots(figsize=(10, 6))
colors = ['#d62728' if f < 50 else '#2ca02c' if f > 80 else '#1f77b4' for f in f1_egr]
bars = ax.bar(attacks, f1_egr, color=colors, edgecolor='k', linewidth=0.5)
for b, v in zip(bars, f1_egr):
    ax.text(b.get_x()+b.get_width()/2, v+1, f'{v}%', ha='center', fontsize=10, fontweight='bold')

ax.axhline(y=np.mean(f1_egr), color='red', linestyle='--', alpha=0.6, label=f'Mean = {np.mean(f1_egr):.1f}%')
ax.axhline(y=85, color='green', linestyle=':', alpha=0.6, label='Target 85%')
ax.set_ylabel('F1 Score (%)', fontsize=12)
ax.set_xlabel('Attack Type', fontsize=12)
ax.set_title('E-GraphSAGE: Large F1 Variance Across Attack Types\n(entangled feature distributions cause inconsistency)', fontsize=13, fontweight='bold')
ax.set_ylim(0, 105)
ax.legend(loc='upper left')
ax.grid(axis='y', alpha=0.3)

fig.tight_layout()
out = 'outputs/rcb/repo/workspaces/Information_003_20261012/outputs/fig2_f1_gap.png'
fig.savefig(out, dpi=100, bbox_inches='tight', facecolor='white')
plt.close(fig)
print(f'[saved] {out} ({Path(out).stat().st_size/1024:.1f} KB)')
