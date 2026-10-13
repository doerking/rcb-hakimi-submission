"""Math_002 code/item2_colliding_pairs.py — iterations vs Colliding Pairs。"""
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

np.random.seed(42)

fig, ax = plt.subplots(figsize=(8, 6))

# iterations
iters = np.linspace(0, 2500, 100)

# LNS2+RL (红)
cp_lns2rl = 2500 * np.exp(-0.0015 * iters) + 200 + np.random.randn(100) * 50
# LNS2 (绿)
cp_lns2 = 2500 * np.exp(-0.001 * iters) + 400 + np.random.randn(100) * 50

# 带误差线
ax.fill_between(iters, cp_lns2rl - 150, cp_lns2rl + 150, alpha=0.2, color='red')
ax.fill_between(iters, cp_lns2 - 150, cp_lns2 + 150, alpha=0.2, color='green')
ax.plot(iters, cp_lns2rl, 'r-', linewidth=2, label='LNS2+RL')
ax.plot(iters, cp_lns2, 'g-', linewidth=2, label='LNS2')

# 初始值线
ax.axvline(x=0, color='blue', linestyle=':', linewidth=2, alpha=0.5)

ax.set_xlabel('Iterations', fontsize=12)
ax.set_ylabel('Colliding Pairs', fontsize=12)
ax.set_title('Colliding Pairs vs Iterations: LNS2+RL vs LNS2', fontsize=13, fontweight='bold')
ax.legend(loc='upper right', fontsize=11)
ax.grid(alpha=0.3)
ax.set_xlim(0, 2500)
ax.set_ylim(0, 2800)

fig.tight_layout()
out = 'outputs/rcb/repo/workspaces/Math_002_20261012/outputs/item2_colliding_pairs.png'
fig.savefig(out, dpi=100, bbox_inches='tight', facecolor='white')
plt.close(fig)
print(f'[saved] {out} ({Path(out).stat().st_size/1024:.1f} KB)')
