"""Figure 2: Dual graph VAE architecture (clean schematic)."""
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Ellipse, Circle, Rectangle
from scipy.stats import multivariate_normal

from utils import set_style, REPORT_IMG

set_style()

fig, ax = plt.subplots(figsize=(14, 4.5))
ax.set_xlim(0, 140)
ax.set_ylim(0, 45)
ax.axis('off')

def draw_molecule(ax, x, y, color='#9DB4D0', edgecolor='#2C5F87', n_units=4,
                 is_epoxide=False):
    """Draw a simplified polymer chain with functional groups."""
    for i in range(n_units):
        cx = x + i * 4
        ax.add_patch(Ellipse((cx, y), 3, 1.2, facecolor=color, edgecolor=edgecolor, lw=0.7))
        if i < n_units - 1:
            ax.plot([cx + 1.5, cx + 2.5], [y, y], color=edgecolor, lw=1)
    if is_epoxide:
        # Add epoxide rings
        for i in range(n_units):
            cx = x + i * 4
            ax.add_patch(Circle((cx, y), 0.6, facecolor='none', edgecolor=edgecolor, lw=0.7))
            ax.text(cx, y + 0.1, 'O', fontsize=4, ha='center', va='center', color=edgecolor)

def draw_nn(ax, x, y, layers, node_colors, line_color, height=8):
    """Draw a small neural network diagram."""
    n_layers = len(layers)
    layer_spacing = 4
    for li, n_nodes in enumerate(layers):
        for nj in range(n_nodes):
            node_x = x + li * layer_spacing
            node_y = y + (nj - (n_nodes - 1) / 2) * (height / max(n_nodes, 3))
            ax.add_patch(Circle((node_x, node_y), 0.6, facecolor=node_colors[li],
                              edgecolor=line_color, lw=0.8))
        # Draw connections
        if li > 0:
            prev_n = layers[li-1]
            prev_x = x + (li-1) * layer_spacing
            prev_positions = [y + (nj - (prev_n - 1) / 2) * (height / max(prev_n, 3))
                            for nj in range(prev_n)]
            cur_positions = [y + (nj - (n_nodes - 1) / 2) * (height / max(n_nodes, 3))
                           for nj in range(n_nodes)]
            for py in prev_positions:
                for cy in cur_positions:
                    ax.plot([prev_x + 0.6, node_x - 0.6], [py, cy],
                          color=line_color, lw=0.3, alpha=0.5)

# ===================================================================
# LEFT: Input molecules
# ===================================================================
ax.text(7, 42, 'Acid: $G^a$', fontsize=9, color='#2C5F87', fontweight='bold', ha='center')
draw_molecule(ax, 2, 38, color='#9DB4D0', edgecolor='#2C5F87', n_units=4)
draw_molecule(ax, 2, 32, color='#B4C9E1', edgecolor='#2C5F87', n_units=4)

ax.text(7, 20, 'Epoxide: $G^e$', fontsize=9, color='#B5783A', fontweight='bold', ha='center')
draw_molecule(ax, 2, 14, color='#E6B877', edgecolor='#B5783A', n_units=4, is_epoxide=True)
draw_molecule(ax, 2, 8, color='#F0CFA6', edgecolor='#B5783A', n_units=4, is_epoxide=True)

# ===================================================================
# ACID ENCODER (top)
# ===================================================================
ax.text(33, 42, 'Encoder $\\phi_a$', ha='center', fontsize=8, color='#2C5F87', fontweight='bold')
draw_nn(ax, 25, 35, [4, 6, 6, 3], ['#9DB4D0']*4, '#2C5F87', height=7)
ax.text(42, 35, '$\\mu^a, \\log\\sigma^a$', fontsize=7, color='#2C5F87',
       va='center', ha='left')

# ===================================================================
# EPOXIDE ENCODER (bottom)
# ===================================================================
ax.text(33, 20, 'Encoder $\\phi_e$', ha='center', fontsize=8, color='#B5783A', fontweight='bold')
draw_nn(ax, 25, 11, [4, 6, 6, 3], ['#E6B877']*4, '#B5783A', height=7)
ax.text(42, 11, '$\\mu^e, \\log\\sigma^e$', fontsize=7, color='#B5783A',
       va='center', ha='left')

# ===================================================================
# Arrows to latent space
# ===================================================================
ax.annotate('', xy=(55, 35), xytext=(48, 35),
           arrowprops=dict(arrowstyle='->', color='#2C5F87', lw=1.5, mutation_scale=15))
ax.annotate('', xy=(55, 11), xytext=(48, 11),
           arrowprops=dict(arrowstyle='->', color='#B5783A', lw=1.5, mutation_scale=15))

# ===================================================================
# CENTER: Latent space (probabilistic)
# ===================================================================
lat_x, lat_y = 68, 23
ax.text(lat_x, 42, 'Probabilistic latent space', ha='center', fontsize=9, fontweight='bold')
ax.text(lat_x, 39, '$z \\sim \\mathcal{N}(\\mu, \\sigma^2)$', ha='center', fontsize=8)

# Latent box background
ax.add_patch(FancyBboxPatch((lat_x-12, lat_y-8), 24, 16,
                           boxstyle='round,pad=0.2', facecolor='#F0F5FA',
                           edgecolor='#888', lw=1))

# 2D Gaussian contours
x = np.linspace(lat_x-10, lat_x+10, 80)
y = np.linspace(lat_y-6, lat_y+6, 80)
X, Y = np.meshgrid(x, y)
mean = [lat_x, lat_y]
cov = [[4, 0.5], [0.5, 2]]
rv = multivariate_normal(mean, cov)
X_flat, Y_flat = X.flatten(), Y.flatten()
pts = np.vstack([X_flat, Y_flat]).T
Z = rv.pdf(pts).reshape(X.shape)

levels = np.linspace(Z.min(), Z.max(), 8)[1:]
ax.contour(X, Y, Z, levels=levels, colors='#2C5F87', linewidths=0.8, alpha=0.7)
ax.contourf(X, Y, Z, levels=levels, colors='#9DB4D0', alpha=0.25)

# Mark mean
ax.plot(lat_x, lat_y, 'r*', ms=14, color='#C82323', zorder=5)
ax.text(lat_x + 1.2, lat_y + 1.2, '$z$', fontsize=10, color='#C82323', fontweight='bold')

# Overlap annotation
ax.annotate('overlapping\ndimensions', xy=(lat_x+3, lat_y-3), xytext=(lat_x+5, lat_y-7),
           fontsize=6, color='#666', ha='center',
           arrowprops=dict(arrowstyle='->', color='#666', lw=0.8))

# ===================================================================
# PROPERTY PREDICTOR (below latent)
# ===================================================================
pred_x, pred_y = 68, 5
ax.text(pred_x, 12, 'Property predictor: $T_g = \\mathcal{F}(z)$',
       ha='center', fontsize=8, fontweight='bold')
# Small NN
draw_nn(ax, 60, pred_y, [3, 4, 2, 1], ['#9DB4D0', '#AAB7CC', '#B4C9E1', '#C82323'],
       '#555', height=3)
ax.annotate('', xy=(82, pred_y), xytext=(79, pred_y),
           arrowprops=dict(arrowstyle='->', color='#C82323', lw=1.3, mutation_scale=12))
ax.text(84, pred_y, '$T_g$', fontsize=11, color='#C82323', fontweight='bold', va='center')

# Arrow from latent to predictor
ax.annotate('', xy=(pred_x, 9), xytext=(lat_x, lat_y-7),
           arrowprops=dict(arrowstyle='->', color='#C82323', lw=1.3,
                         connectionstyle='arc3,rad=-0.2'))

# ===================================================================
# DECODERS (right)
# ===================================================================
# Acid decoder
ax.text(95, 42, 'Decoder $\\theta_a$', ha='center', fontsize=8, color='#2C5F87', fontweight='bold')
draw_nn(ax, 88, 35, [3, 6, 6, 4], ['#9DB4D0']*4, '#2C5F87', height=7)

# Epoxide decoder
ax.text(95, 20, 'Decoder $\\theta_e$', ha='center', fontsize=8, color='#B5783A', fontweight='bold')
draw_nn(ax, 88, 11, [3, 6, 6, 4], ['#E6B877']*4, '#B5783A', height=7)

# Arrows from latent to decoders
ax.annotate('', xy=(88, 35), xytext=(78, 30),
           arrowprops=dict(arrowstyle='->', color='#2C5F87', lw=1.3, mutation_scale=12))
ax.annotate('', xy=(88, 11), xytext=(78, 16),
           arrowprops=dict(arrowstyle='->', color='#B5783A', lw=1.3, mutation_scale=12))

# ===================================================================
# RIGHT: Reconstructed molecules
# ===================================================================
ax.text(118, 42, '$G^{a\\prime}$ (recon.)', fontsize=8, color='#2C5F87', fontweight='bold', ha='center')
draw_molecule(ax, 110, 38, color='#9DB4D0', edgecolor='#2C5F87', n_units=4)
draw_molecule(ax, 110, 32, color='#B4C9E1', edgecolor='#2C5F87', n_units=4)

ax.text(118, 20, '$G^{e\\prime}$ (recon.)', fontsize=8, color='#B5783A', fontweight='bold', ha='center')
draw_molecule(ax, 110, 14, color='#E6B877', edgecolor='#B5783A', n_units=4, is_epoxide=True)
draw_molecule(ax, 110, 8, color='#F0CFA6', edgecolor='#B5783A', n_units=4, is_epoxide=True)

# Arrows from decoders to reconstructions
ax.annotate('', xy=(110, 38), xytext=(106, 35),
           arrowprops=dict(arrowstyle='->', color='#2C5F87', lw=1.2, mutation_scale=10))
ax.annotate('', xy=(110, 14), xytext=(106, 11),
           arrowprops=dict(arrowstyle='->', color='#B5783A', lw=1.2, mutation_scale=10))

# ===================================================================
# Save
# ===================================================================
os.makedirs(REPORT_IMG, exist_ok=True)
out_path = os.path.join(REPORT_IMG, '__2.png')
fig.savefig(out_path, dpi=200, bbox_inches='tight', facecolor='white')
print(f'Saved: {out_path}')
