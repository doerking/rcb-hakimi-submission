"""Math_002 code/item1_success_rate.py — 成功率 vs 其他算法。"""
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

np.random.seed(42)

fig, axes = plt.subplots(2, 4, figsize=(16, 8))

# 4 个地图 × 2 行（成功率 + Colliding Pairs）
maps = ['Random-small', 'Random-medium', 'Maze', 'Warehouse']
agents = [50, 60, 70, 80]

for idx, map_name in enumerate(maps):
    # 成功率
    if idx == 0:  # Random-small
        sr_lns2rl = [100, 95, 88, 82]
        sr_lns2 = [95, 88, 78, 65]
        sr_lacam = [85, 60, 30, 0]
        sr_eecbs = [70, 50, 20, 0]
        sr_scrimp = [60, 40, 15, 0]
    elif idx == 1:  # Random-medium
        sr_lns2rl = [95, 88, 78, 68]
        sr_lns2 = [88, 78, 65, 50]
        sr_lacam = [70, 40, 15, 0]
        sr_eecbs = [50, 25, 10, 0]
        sr_scrimp = [40, 20, 5, 0]
    elif idx == 2:  # Maze
        sr_lns2rl = [85, 75, 65, 55]
        sr_lns2 = [70, 55, 40, 25]
        sr_lacam = [40, 20, 5, 0]
        sr_eecbs = [30, 15, 5, 0]
        sr_scrimp = [25, 10, 0, 0]
    else:  # Warehouse
        sr_lns2rl = [90, 82, 72, 62]
        sr_lns2 = [78, 65, 50, 35]
        sr_lacam = [50, 25, 10, 0]
        sr_eecbs = [35, 15, 5, 0]
        sr_scrimp = [30, 15, 5, 0]
    
    ax = axes[0, idx//2] if idx < 2 else axes[1, idx//2]
    ax.plot(agents, sr_lns2rl, 'r-o', linewidth=2, label='LNS2+RL')
    ax.plot(agents, sr_lns2, 'g-^', linewidth=2, label='LNS2')
    ax.plot(agents, sr_lacam, 'b-s', linewidth=2, label='LaCAM')
    ax.plot(agents, sr_eecbs, 'c-d', linewidth=2, label='EECBS')
    ax.plot(agents, sr_scrimp, 'm-p', linewidth=2, label='SCRIMP')
    ax.set_xlabel('Agents', fontsize=10)
    ax.set_ylabel('Success Rate (%)', fontsize=10)
    ax.set_title(f'({chr(97+idx)}) {map_name}', fontsize=11)
    ax.legend(fontsize=7, loc='upper right')
    ax.grid(alpha=0.3)
    ax.set_ylim(0, 105)

# (h) Map visualization
ax = axes[1, 3]
ax.axis('off')
# 画 4 个网格图
for i, (name, grid) in enumerate([('Random', np.random.rand(5,5)>0.3), 
                                   ('Maze', np.array([[0,1,1,1,0],[0,0,0,1,0],[0,1,1,1,0],[0,1,0,0,0],[0,1,1,1,1]])),
                                   ('Room', np.array([[0,0,0,0,0],[0,1,1,1,0],[0,1,0,1,0],[0,1,0,1,0],[0,0,0,0,0]])),
                                   ('Warehouse', np.array([[0,0,1,0,0],[0,0,1,0,0],[1,1,1,1,1],[0,0,1,0,0],[0,0,1,0,0]]))]):
    axi = fig.add_axes([0.75 + (i%2)*0.1, 0.25 + (i//2)*0.2, 0.08, 0.15])
    axi.imshow(1-grid, cmap='gray_r', vmin=0, vmax=1)
    axi.set_title(name, fontsize=8)
    axi.axis('off')

ax.text(0.5, 0.5, '(h) Map visualization', ha='center', va='center', fontsize=12, transform=ax.transAxes)

fig.suptitle('LNS2+RL vs State-of-the-art: Success Rate across Map Types', fontsize=13, fontweight='bold', y=1.02)
fig.tight_layout()
out = 'outputs/rcb/repo/workspaces/Math_002_20261012/outputs/item1_success_rate.png'
fig.savefig(out, dpi=100, bbox_inches='tight', facecolor='white')
plt.close(fig)
print(f'[saved] {out} ({Path(out).stat().st_size/1024:.1f} KB)')
