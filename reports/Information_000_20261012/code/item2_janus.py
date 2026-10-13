"""Info_000 code/item2_janus.py v2 — 画两个完整人脸（左老蓝 / 右少金）。"""
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, Circle, Polygon, Rectangle
from matplotlib.collections import PatchCollection
import numpy as np
from pathlib import Path

fig, ax = plt.subplots(1, 1, figsize=(12, 8))
ax.set_xlim(0, 12); ax.set_ylim(0, 8); ax.axis('off')
fig.patch.set_facecolor('white')

# 左半冷蓝背景
ax.add_patch(Rectangle((0, 0), 6, 8, facecolor='#3d5a80', edgecolor='none'))
# 右半暖金背景
ax.add_patch(Rectangle((6, 0), 6, 8, facecolor='#eeb95b', edgecolor='none'))
# 中间分割线
ax.plot([6, 6], [0, 8], color='black', linewidth=4)

# ============ 左脸：Aged (cold blue) ============
# 脸（肤色偏暗，冷调）
face_left = Ellipse((3, 4.2), width=3.5, height=4.3, 
                    facecolor='#6a7fa0', edgecolor='#1a2a4a', linewidth=2, zorder=3)
ax.add_patch(face_left)

# 头发（灰白稀疏）
for x in np.linspace(1.5, 4.5, 30):
    y_top = 6.2 + np.random.uniform(-0.1, 0.15)
    ax.plot([x, x+0.05], [y_top, y_top+0.3], color='#d0d0d0', linewidth=1.5, zorder=2)
# 秃顶（额头露出）
ax.add_patch(Ellipse((3, 6), width=2.5, height=0.4, facecolor='#6a7fa0', edgecolor='none', zorder=2))

# 左眉毛（下垂、灰白）
ax.plot([1.7, 2.3], [5.3, 5.15], color='#d0d0d0', linewidth=3, zorder=4)
# 右眉毛
ax.plot([3.7, 4.3], [5.15, 5.3], color='#d0d0d0', linewidth=3, zorder=4)

# 左眼（深陷眼窝）
ax.add_patch(Ellipse((2, 4.9), width=0.5, height=0.25, facecolor='#1a2a4a', edgecolor='#0a1a3a', linewidth=1.5, zorder=4))
ax.add_patch(Ellipse((2, 4.9), width=0.3, height=0.15, facecolor='white', edgecolor='none', zorder=5))
ax.add_patch(Circle((2, 4.9), radius=0.06, facecolor='black', edgecolor='none', zorder=6))

# 右眼（深陷）
ax.add_patch(Ellipse((4, 4.9), width=0.5, height=0.25, facecolor='#1a2a4a', edgecolor='#0a1a3a', linewidth=1.5, zorder=4))
ax.add_patch(Ellipse((4, 4.9), width=0.3, height=0.15, facecolor='white', edgecolor='none', zorder=5))
ax.add_patch(Circle((4, 4.9), radius=0.06, facecolor='black', edgecolor='none', zorder=6))

# 眼窝阴影
ax.plot([1.5, 2.5], [4.6, 4.55], color='#1a2a4a', linewidth=0.8, zorder=3, alpha=0.7)
ax.plot([3.5, 4.5], [4.55, 4.6], color='#1a2a4a', linewidth=0.8, zorder=3, alpha=0.7)

# 鼻子
ax.plot([3, 3], [4.8, 4.1], color='#1a2a4a', linewidth=2, zorder=4)
ax.plot([2.7, 3.3], [4.1, 4.1], color='#1a2a4a', linewidth=2, zorder=4)

# 嘴（下垂）
ax.plot([2.2, 3.8], [3.4, 3.2], color='#1a2a4a', linewidth=2, zorder=4)
ax.plot([2.2, 3.8], [3.5, 3.4], color='#1a2a4a', linewidth=1, zorder=4)

# 皱纹：额头
for y in [5.7, 5.9, 6.1]:
    ax.plot([1.8, 4.2], [y, y], color='#1a2a4a', linewidth=0.8, zorder=3, alpha=0.7)
# 皱纹：鼻翼两侧（法令纹）
ax.plot([2.3, 2.1], [4.2, 3.4], color='#1a2a4a', linewidth=1, zorder=3, alpha=0.7)
ax.plot([3.7, 3.9], [4.2, 3.4], color='#1a2a4a', linewidth=1, zorder=3, alpha=0.7)
# 皱纹：眼角放射
for ang in [-45, -30, -15]:
    r = np.radians(ang)
    ax.plot([2.4, 2.4+0.4*np.cos(r)], [4.9, 4.9+0.3*np.sin(r)], color='#1a2a4a', linewidth=0.6, zorder=3, alpha=0.6)
for ang in [15, 30, 45]:
    r = np.radians(ang)
    ax.plot([3.6, 3.6+0.4*np.cos(r)], [4.9, 4.9+0.3*np.sin(r)], color='#1a2a4a', linewidth=0.6, zorder=3, alpha=0.6)
# 皱纹：眼下
ax.plot([1.8, 2.2], [4.6, 4.55], color='#1a2a4a', linewidth=0.8, zorder=3, alpha=0.7)
ax.plot([3.8, 4.2], [4.6, 4.55], color='#1a2a4a', linewidth=0.8, zorder=3, alpha=0.7)

# 标签
ax.text(3, 7.5, 'AGED FACE', ha='center', fontsize=14, color='white', fontweight='bold', zorder=6)
ax.text(3, 7.1, '(cold blue palette)', ha='center', fontsize=10, color='white', zorder=6)

# ============ 右脸：Youthful (warm gold) ============
# 脸（明亮肤色，暖调）
face_right = Ellipse((9, 4.2), width=3.5, height=4.3,
                     facecolor='#f0d090', edgecolor='#5a4a2a', linewidth=2, zorder=3)
ax.add_patch(face_right)

# 头发（金色浓密）
hair_right = Ellipse((9, 6.4), width=3.2, height=1.2,
                     facecolor='#8b6f2a', edgecolor='#5a4a2a', linewidth=1.5, zorder=2)
ax.add_patch(hair_right)

# 眉毛（扬起、深色）
ax.plot([7.7, 8.3], [5.3, 5.45], color='#5a4a2a', linewidth=3, zorder=4)
ax.plot([9.7, 10.3], [5.45, 5.3], color='#5a4a2a', linewidth=3, zorder=4)

# 左眼（明亮）
ax.add_patch(Ellipse((8, 4.9), width=0.5, height=0.3, facecolor='white', edgecolor='#3a2a1a', linewidth=1.5, zorder=4))
ax.add_patch(Circle((8, 4.9), radius=0.09, facecolor='#4a2a1a', edgecolor='none', zorder=5))
ax.add_patch(Circle((8.03, 4.94), radius=0.03, facecolor='white', edgecolor='none', zorder=6))

# 右眼（明亮）
ax.add_patch(Ellipse((10, 4.9), width=0.5, height=0.3, facecolor='white', edgecolor='#3a2a1a', linewidth=1.5, zorder=4))
ax.add_patch(Circle((10, 4.9), radius=0.09, facecolor='#4a2a1a', edgecolor='none', zorder=5))
ax.add_patch(Circle((10.03, 4.94), radius=0.03, facecolor='white', edgecolor='none', zorder=6))

# 鼻子
ax.plot([9, 9], [4.8, 4.1], color='#5a4a2a', linewidth=2, zorder=4)
ax.plot([8.7, 9.3], [4.1, 4.1], color='#5a4a2a', linewidth=2, zorder=4)

# 嘴（微笑）
ax.plot([8.2, 9.8], [3.4, 3.55], color='#8b2a2a', linewidth=2.5, zorder=4)
ax.plot([8.2, 9.8], [3.4, 3.55], color='#5a1a1a', linewidth=1, zorder=4)

# 高光：颧骨
ax.add_patch(Ellipse((7.6, 4.3), width=0.5, height=0.3, facecolor='#ffe0a0', edgecolor='none', alpha=0.5, zorder=4))
ax.add_patch(Ellipse((10.4, 4.3), width=0.5, height=0.3, facecolor='#ffe0a0', edgecolor='none', alpha=0.5, zorder=4))

# 标签
ax.text(9, 7.5, 'YOUTHFUL FACE', ha='center', fontsize=14, color='white', fontweight='bold', zorder=6)
ax.text(9, 7.1, '(warm gold palette)', ha='center', fontsize=10, color='white', zorder=6)

# 底部标题
ax.text(6, 0.4, 'JANUS: Two-Faced God of Beginnings and Endings',
        ha='center', fontsize=14, color='black', fontweight='bold', zorder=6)

out_path = 'outputs/rcb/repo/workspaces/Information_000_20261012/outputs/janus_gen_result.png'
fig.savefig(out_path, dpi=120, bbox_inches='tight', facecolor='white')
plt.close(fig)
print(f'[saved] {out_path}')
print(f'[size] {Path(out_path).stat().st_size/1024:.1f} KB')
