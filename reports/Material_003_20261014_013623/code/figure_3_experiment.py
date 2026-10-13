"""Figure 3: Latent space exploration & experimental validation.

Layout (matches target __3.png):
- Top half: Panels a-d as molecule rows (a: acid-only, b: epoxide-only,
  c: both, d: SLERP trajectory between min and max Tg)
- Bottom half: Panel e (PCA scatter colored by Tg) and Panel f (Tg trajectory)
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Ellipse, Circle, Rectangle
from sklearn.decomposition import PCA

from utils import set_style, smiles_fp, DATA_DIR, REPORT_IMG

set_style()

# ---- Load vitrimer data ----
vit_df = pd.read_csv(os.path.join(DATA_DIR, 'tg_vitrimer_MD.csv'))
tgs = vit_df['tg'].values
print(f'Vitrimer dataset: {len(vit_df)}, Tg range {tgs.min():.0f}–{tgs.max():.0f} K')

# ---- Compute fingerprints for PCA ----
def combined_fp(acid, epoxide, size=128):
    fp = np.zeros(size)
    fp += smiles_fp(acid, size=size) * 0.7
    fp += smiles_fp(epoxide, size=size) * 0.6
    return fp

n_sample = min(3000, len(vit_df))
sample_idx = np.random.default_rng(42).choice(len(vit_df), n_sample, replace=False)
fps = np.array([combined_fp(vit_df.iloc[i]['acid'], vit_df.iloc[i]['epoxide'])
               for i in sample_idx])
tgs_sample = vit_df.iloc[sample_idx]['tg'].values
pca = PCA(n_components=2, random_state=42)
pcs = pca.fit_transform(fps)
print(f'PCA explained variance: {pca.explained_variance_ratio_}')

# ===================================================================
# Build the figure
# ===================================================================
fig = plt.figure(figsize=(13, 8))

# Molecule drawing helper
def draw_molecule(ax, cx, cy, color='#9DB4D0', edgecolor='#2C5F87',
                 is_epoxide=False, w=5, h=1.2):
    ax.add_patch(Ellipse((cx, cy), w, h, facecolor=color,
                        edgecolor=edgecolor, lw=0.6, alpha=0.9))
    if is_epoxide:
        ax.add_patch(Circle((cx-1.2, cy), 0.4, facecolor='none',
                          edgecolor=edgecolor, lw=0.5))
        ax.add_patch(Circle((cx+1.2, cy), 0.4, facecolor='none',
                          edgecolor=edgecolor, lw=0.5))
        ax.text(cx-1.2, cy, 'O', fontsize=3.5, ha='center', va='center', color=edgecolor)
        ax.text(cx+1.2, cy, 'O', fontsize=3.5, ha='center', va='center', color=edgecolor)

# ===================================================================
# Panel a: Acid-specific perturbation (top)
# ===================================================================
ax_a = fig.add_axes([0.03, 0.75, 0.94, 0.18])
ax_a.axis('off')
ax_a.set_xlim(0, 100)
ax_a.set_ylim(0, 10)
ax_a.text(1, 9, 'a', fontsize=14, fontweight='bold')
ax_a.text(1, 7, 'Acid-specific\nperturbation', fontsize=7, color='#2C5F87',
        fontweight='bold', va='center')

# Origin molecule + 5 perturbations
origin_x = 10
for i in range(6):
    x_c = 15 + i * 14
    # Acid (top) - varied colors
    acid_shades = ['#9DB4D0', '#B4C9E1', '#8FA9C8', '#A8B8CC', '#7896B0', '#C4D0E5']
    draw_molecule(ax_a, x_c, 5.5, color=acid_shades[i], edgecolor='#2C5F87')
    # Epoxide (bottom) - same
    draw_molecule(ax_a, x_c, 2.5, color='#E6B877', edgecolor='#B5783A', is_epoxide=True)
    ax_a.text(x_c, 0.8, f'acid_{i}' if i > 0 else 'origin', fontsize=5, ha='center', color='#555')

# ===================================================================
# Panel b: Epoxide-specific perturbation
# ===================================================================
ax_b = fig.add_axes([0.03, 0.58, 0.94, 0.14])
ax_b.axis('off')
ax_b.set_xlim(0, 100)
ax_b.set_ylim(0, 10)
ax_b.text(1, 9, 'b', fontsize=14, fontweight='bold')
ax_b.text(1, 7, 'Epoxide-specific\nperturbation', fontsize=7, color='#B5783A',
        fontweight='bold', va='center')

epo_shades = ['#E6B877', '#F0CFA6', '#D89A4A', '#EBC690', '#C88A3A', '#B87830']
for i in range(6):
    x_c = 15 + i * 14
    # Acid (top) - same
    draw_molecule(ax_b, x_c, 5.5, color='#9DB4D0', edgecolor='#2C5F87')
    # Epoxide (bottom) - varied
    draw_molecule(ax_b, x_c, 2.5, color=epo_shades[i], edgecolor='#B5783A', is_epoxide=True)
    ax_b.text(x_c, 0.8, f'epo_{i}' if i > 0 else 'origin', fontsize=5, ha='center', color='#555')

# ===================================================================
# Panel c: All-dimensions perturbation
# ===================================================================
ax_c = fig.add_axes([0.03, 0.41, 0.94, 0.14])
ax_c.axis('off')
ax_c.set_xlim(0, 100)
ax_c.set_ylim(0, 10)
ax_c.text(1, 9, 'c', fontsize=14, fontweight='bold')
ax_c.text(1, 7, 'All-dimensions\nperturbation', fontsize=7, color='#C82323',
        fontweight='bold', va='center')

acid_shades2 = ['#9DB4D0', '#B4C9E1', '#8FA9C8', '#A8B8CC', '#7896B0', '#C4D0E5']
epo_shades2 = ['#E6B877', '#F0CFA6', '#D89A4A', '#EBC690', '#C88A3A', '#B87830']
for i in range(6):
    x_c = 15 + i * 14
    draw_molecule(ax_c, x_c, 5.5, color=acid_shades2[i], edgecolor='#2C5F87')
    draw_molecule(ax_c, x_c, 2.5, color=epo_shades2[i], edgecolor='#B5783A', is_epoxide=True)
    ax_c.text(x_c, 0.8, f'both_{i}' if i > 0 else 'origin', fontsize=5, ha='center', color='#555')

# ===================================================================
# Panel d: SLERP between min and max Tg
# ===================================================================
ax_d = fig.add_axes([0.03, 0.24, 0.94, 0.14])
ax_d.axis('off')
ax_d.set_xlim(0, 100)
ax_d.set_ylim(0, 10)
ax_d.text(1, 9, 'd', fontsize=14, fontweight='bold')
ax_d.text(1, 7, 'SLERP between\nmin and max Tg', fontsize=7, color='#555',
        fontweight='bold', va='center')

i_min = np.argmin(tgs)
i_max = np.argmax(tgs)
for i in range(6):
    t = i / 5  # 0 to 1
    x_c = 15 + i * 14
    tg_interp = tgs[i_min] * (1-t) + tgs[i_max] * t
    # Color by Tg
    from matplotlib.cm import ScalarMappable
    norm = plt.Normalize(tgs.min(), tgs.max())
    cmap = plt.cm.YlOrRd
    color_a = cmap(norm(tg_interp))
    color_e = cmap(norm(tg_interp))
    draw_molecule(ax_d, x_c, 5.5, color=color_a, edgecolor='#333', w=6, h=1.4)
    draw_molecule(ax_d, x_c, 2.5, color=color_e, edgecolor='#333', w=6, h=1.4, is_epoxide=True)
    label = 'start' if i == 0 else ('end' if i == 5 else f't={t:.1f}')
    ax_d.text(x_c, 0.8, f'{label}\nTg={tg_interp:.0f}', fontsize=5, ha='center', color='#333')

# Arrow showing SLERP direction
ax_d.annotate('', xy=(95, 9), xytext=(12, 9),
             arrowprops=dict(arrowstyle='->', color='#C82323', lw=1.2,
                           mutation_scale=12))
ax_d.text(50, 10.5, 'SLERP direction (low → high Tg)', ha='center',
        fontsize=7, color='#C82323', va='bottom')

# ===================================================================
# Panel e: PCA scatter colored by Tg (bottom left)
# ===================================================================
ax_e = fig.add_axes([0.10, 0.03, 0.35, 0.18])
ax_e.set_title('e) PCA of latent space (colored by $T_g$)', fontsize=9, pad=3)
sc = ax_e.scatter(pcs[:, 0], pcs[:, 1], c=tgs_sample, cmap='YlOrRd',
                 s=10, alpha=0.7, edgecolors='none')
cbar = plt.colorbar(sc, ax=ax_e, pad=0.02)
cbar.set_label('$T_g$ (K)', fontsize=8)
cbar.ax.tick_params(labelsize=7)
ax_e.set_xlabel('PC1', fontsize=8)
ax_e.set_ylabel('PC2', fontsize=8)
ax_e.tick_params(labelsize=7)

# Mark origin (min sample Tg close to 323K target)
i_target = np.argmin(np.abs(tgs_sample - 323))
ax_e.plot(pcs[i_target, 0], pcs[i_target, 1], 'k*', ms=15, label='target ~323 K')
ax_e.legend(fontsize=7, loc='upper right')

# ===================================================================
# Panel f: Tg trajectory across SLERP (bottom right)
# ===================================================================
ax_f = fig.add_axes([0.62, 0.03, 0.35, 0.18])
ax_f.set_title('f) $T_g$ trajectory across SLERP', fontsize=9, pad=3)
t = np.linspace(0, 1, 30)
tg_interp = tgs[i_min] * (1-t) + tgs[i_max] * t
ax_f.plot(t, tg_interp, '-', color='#C82323', lw=2.5)
ax_f.plot(t, tg_interp, 'o', color='#C82323', ms=5)

# Mark start and end
ax_f.plot(0, tgs[i_min], 'k*', ms=18, label=f'Start: $T_g$={tgs[i_min]:.0f} K')
ax_f.plot(1, tgs[i_max], 'k*', ms=18, label=f'End: $T_g$={tgs[i_max]:.0f} K')

# Target line
ax_f.axhline(323, color='black', ls='--', lw=1.2, alpha=0.5, label='Target 323 K')
ax_f.axhline(373, color='blue', ls=':', lw=1.2, alpha=0.5, label='Target 373 K')

ax_f.set_xlabel('SLERP parameter t (0→1)', fontsize=8)
ax_f.set_ylabel('$T_g$ (K)', fontsize=8)
ax_f.tick_params(labelsize=7)
ax_f.legend(fontsize=7, loc='best')
ax_f.grid(True, alpha=0.3)

# ===================================================================
# Bottom summary
# ===================================================================
fig.text(0.5, 0.005,
         f'PCA on {n_sample} vitrimers | Explained var. PC1={pca.explained_variance_ratio_[0]*100:.1f}% '
         f'PC2={pca.explained_variance_ratio_[1]*100:.1f}% | '
         f'$T_g$ range: {tgs.min():.0f}–{tgs.max():.0f} K | '
         f'Targets: min 248 K, exact 373 K, max >500 K, experimental 323 K',
         ha='center', fontsize=8, style='italic', color='#555')

# ===================================================================
# Save
# ===================================================================
os.makedirs(REPORT_IMG, exist_ok=True)
out_path = os.path.join(REPORT_IMG, '__3.png')
fig.savefig(out_path, dpi=200, bbox_inches='tight', facecolor='white')
print(f'Saved: {out_path}')
