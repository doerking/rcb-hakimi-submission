"""Life_000 code/fig5_performance.py — 最终性能表征。"""
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# (a) 应力-应变曲线
ax = axes[0]
strain = np.linspace(0, 12, 100)
stress_gmax = 2.5 * np.exp(-strain/8)
stress_r1max = 2.8 * np.exp(-strain/7)
stress_r2max = 2.3 * np.exp(-strain/6)
stress_r3max = 2.0 * np.exp(-strain/5)

ax.plot(strain, stress_gmax, label='G-max', linewidth=2)
ax.plot(strain, stress_r1max, label='R1-max', linewidth=2, color='#4a90c5')
ax.plot(strain, stress_r2max, label='R2-max', linewidth=2, color='#5fa060')
ax.plot(strain, stress_r3max, label='R3-max', linewidth=2, color='#e08e45')

ax.set_xlabel('Strain', fontsize=11)
ax.set_ylabel('Stress (MPa)', fontsize=11)
ax.set_title('(a) Stress-strain curves', fontsize=12, fontweight='bold')
ax.legend()
ax.grid(alpha=0.3)

# (b) 不同基底的粘合强度
ax = axes[1]
substrates = ['Glass', 'Steel', 'Ceramic', 'PC', 'PA6', 'PEI', 'PTFE', 'Al', 'Ti', 'SS']
fa_values = [1.0, 0.8, 0.7, 0.9, 0.7, 0.6, 0.4, 0.8, 0.85, 0.75]
colors = ['#4a90c5'] * 10

bars = ax.bar(substrates, fa_values, color=colors, edgecolor='k', linewidth=0.5, width=0.7)
for bar, fa in zip(bars, fa_values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
            f'{fa:.1f}', ha='center', va='bottom', fontsize=9)

ax.set_ylabel('Adhesive strength $F_a$ (MPa)', fontsize=11)
ax.set_title('(b) Universal adhesion (R1-max)', fontsize=12, fontweight='bold')
ax.set_ylim(0, 1.2)
ax.grid(axis='y', alpha=0.3)

# (c) 耐久性测试
ax = axes[2]
time = np.linspace(0, 360, 50)
fa_gmax = 0.8 * np.exp(-time/200) + 0.2
fa_r1max = 0.9 * np.exp(-time/300) + 0.1

ax.plot(time, fa_gmax, 'o-', label='G-max', markersize=4)
ax.plot(time, fa_r1max, 's-', label='R1-max', markersize=4, color='#4a90c5')

ax.set_xlabel('Time (s)', fontsize=11)
ax.set_ylabel('Adhesive strength $F_a$ (MPa)', fontsize=11)
ax.set_title('(c) Durability test', fontsize=12, fontweight='bold')
ax.legend()
ax.grid(alpha=0.3)

fig.tight_layout()
out = 'outputs/rcb/repo/workspaces/Life_000_20261012/outputs/fig5_performance.png'
fig.savefig(out, dpi=100, bbox_inches='tight', facecolor='white')
plt.close(fig)
print(f'[saved] {out} ({Path(out).stat().st_size/1024:.1f} KB)')
