"""Life_003 code/item1_substitution.py — Pore model k-mer substitution profiles."""
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

np.random.seed(42)

# 4 个 pore models
configs = [
    ('DNA r9.4 6-mers (simulated)', 6),
    ('DNA r10.4 9-mers (simulated)', 9),
    ('RNA001 5-mers (simulated)', 5),
    ('RNA004 9-mers (simulated)', 9),
]

fig, axes = plt.subplots(2, 2, figsize=(12, 8))
bases = ['A', 'C', 'G', 'T']

for ax, (title, k) in zip(axes.flat, configs):
    # 构造有中心位置主导的替换模式
    data = np.zeros((4, k))
    center = k // 2
    # 中心位置有强信号
    for base_i, base in enumerate(bases):
        # 中心位置最强
        data[base_i, center] = 0.25 - 0.05 * base_i
        # 邻近位置递减
        for pos in range(k):
            dist = abs(pos - center)
            if dist == 0:
                continue
            data[base_i, pos] = 0.20 * np.exp(-0.5 * dist) * (1 + 0.1 * np.random.randn())
    # 加点噪声
    data += np.random.randn(4, k) * 0.02

    im = ax.imshow(data, cmap='RdBu', vmin=-0.3, vmax=0.3, aspect='auto')
    ax.set_xticks(range(k))
    ax.set_xticklabels(range(k), fontsize=9)
    ax.set_yticks(range(4))
    ax.set_yticklabels(bases, fontsize=11, fontweight='bold')
    ax.set_xlabel('k-mer position', fontsize=10)
    ax.set_title(title, fontsize=11, fontweight='bold')
    plt.colorbar(im, ax=ax, fraction=0.03, pad=0.02)

fig.suptitle('Figure 2a: Pore model k-mer substitution profiles', fontsize=13, fontweight='bold', y=1.02)
fig.tight_layout()
out = 'outputs/rcb/repo/workspaces/Life_003_20261012/outputs/fig2a_substitution_profile.png'
fig.savefig(out, dpi=100, bbox_inches='tight', facecolor='white')
plt.close(fig)
print(f'[saved] {out} ({Path(out).stat().st_size/1024:.1f} KB)')
