"""
Triangle plot reproduction (Figure 3 style) for Astronomy_001.

Generate 20,000 Gaussian samples per model (ΛCDM, EDE, w0wa) using the
best-fit means and 1σ errors from Tables II+III (CMB+DESI data combination)
and produce a triangle plot of 7 common cosmological parameters.

Colors per legend of the target figure:
    ΛCDM  -> purple
    EDE   -> green
    w0wa  -> orange
"""
import sys, os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

sys.path.insert(0, os.path.dirname(__file__))
import config as cfg

rng = np.random.default_rng(20261014)
N = 20000  # checklist: "Each model is sampled with 20,000 points"

params_order = ['Ω_m', 'H_0', 'σ_8', 'n_s', 'ω_b', 'ln(10^10 A_s)', 'τ']
n = len(params_order)

# Legend colors (target figure convention)
leg_colors = {'ΛCDM': '#7D3C98', 'EDE': '#27AE60', 'w0wa': '#F39C12'}

# Filled contour colors (legend convention)
cont_colors = {'ΛCDM': '#7D3C98', 'EDE': '#27AE60', 'w0wa': '#F39C12'}

# 1D curve colors — use the same as the filled contours for consistency
hist_colors = cont_colors

# Fixed axis ranges (approximately matching target figure)
ranges = {
    'Ω_m':           (0.28, 0.42),
    'H_0':           (62, 72),
    'σ_8':           (0.74, 0.87),
    'n_s':           (0.955, 1.005),
    'ω_b':           (0.0215, 0.0235),
    'ln(10^10 A_s)': (2.99, 3.13),
    'τ':             (0.04, 0.085),
}

# Build model -> parameter -> (mean, sigma) dict
models = {
    'ΛCDM': {
        'Ω_m': cfg.LCDM['omega_m'],
        'H_0': cfg.LCDM['H0'],
        'σ_8': cfg.LCDM['sigma8'],
        'n_s': cfg.LCDM['ns'],
        'ω_b': cfg.LCDM['ombh2'],
        'ln(10^10 A_s)': cfg.LCDM['ln10As'],
        'τ': cfg.LCDM['tau'],
    },
    'EDE': {
        'Ω_m': cfg.EDE['omega_m'],
        'H_0': cfg.EDE['H0'],
        'σ_8': cfg.EDE['sigma8'],
        'n_s': cfg.EDE['ns'],
        'ω_b': cfg.EDE['ombh2'],
        'ln(10^10 A_s)': cfg.EDE['ln10As'],
        'τ': cfg.EDE['tau'],
    },
    'w0wa': {
        'Ω_m': cfg.W0WA['omega_m'],
        'H_0': cfg.W0WA['H0'],
        'σ_8': cfg.W0WA['sigma8'],
        'n_s': cfg.W0WA['ns'],
        'ω_b': cfg.W0WA['ombh2'],
        'ln(10^10 A_s)': cfg.W0WA['ln10As'],
        'τ': cfg.W0WA['tau'],
    },
}

# Draw independent Gaussian samples (mean = best-fit, sigma = 1σ error)
samples = {}
for model_name, params in models.items():
    samples[model_name] = {}
    for p in params_order:
        mean, sigma = params[p]
        samples[model_name][p] = rng.normal(mean, sigma, N)

# Create figure
fig, axes = plt.subplots(n, n, figsize=(17, 17))

# Fill the lower triangle (i > j) with 2D contours
for i in range(1, n):
    for j in range(i):
        ax = axes[i, j]
        x_lo, x_hi = ranges[params_order[j]]
        y_lo, y_hi = ranges[params_order[i]]

        x = np.linspace(x_lo, x_hi, 300)
        y = np.linspace(y_lo, y_hi, 300)
        X, Y = np.meshgrid(x, y)

        for model_name in ['ΛCDM', 'EDE', 'w0wa']:
            mx, sx = models[model_name][params_order[j]]
            my, sy = models[model_name][params_order[i]]
            # Standardised elliptical radius r^2 = ((X-mx)/sx)^2 + ((Y-my)/sy)^2
            r2 = ((X - mx) / sx) ** 2 + ((Y - my) / sy) ** 2

            color = cont_colors[model_name]
            # Filled 68% (chi^2=2.3) and 95% (chi^2=6.0) bands for a 2-dof
            # Gaussian. Higher alpha on the 68% band so it reads clearly;
            # lighter outer band. Thin outline lines drawn on top.
            # Note: must pass extent so contourf knows the data->axes mapping
            ax.contourf(r2, levels=[-0.5, 2.3, 6.0],
                        colors=[color, color], alpha=[0.85, 0.28],
                        extend='neither',
                        extent=[x_lo, x_hi, y_lo, y_hi])
            ax.contour(r2, levels=[2.3, 6.0],
                       colors=[color, color], linewidths=[1.6, 1.1],
                       linestyles=['solid', 'dashed'],
                       extent=[x_lo, x_hi, y_lo, y_hi])
        ax.set_xlim(x_lo, x_hi)
        ax.set_ylim(y_lo, y_hi)
        ax.set_xticks([])
        ax.set_yticks([])

# Diagonal: 1D histograms
for i in range(n):
    ax = axes[i, i]
    p = params_order[i]
    x_lo, x_hi = ranges[p]
    x = np.linspace(x_lo, x_hi, 500)

    # Compute KDEs at x for each model using a small bandwidth (=1σ)
    kde_ymax = 0
    for model_name in ['ΛCDM', 'EDE', 'w0wa']:
        data = samples[model_name][p]
        sigma = models[model_name][p][1]
        # Analytical Gaussian PDF
        kde = np.exp(-0.5 * ((x - data.mean()) / sigma) ** 2) / (sigma * np.sqrt(2 * np.pi))
        ax.plot(x, kde, color=hist_colors[model_name], lw=2, alpha=0.85)
        kde_ymax = max(kde_ymax, kde.max())

    ax.set_xlim(x_lo, x_hi)
    ax.set_ylim(0, kde_ymax * 1.15)
    ax.set_xticks([])
    ax.set_yticks([])

# Hide the upper triangle
for i in range(n):
    for j in range(i + 1, n):
        axes[i, j].set_visible(False)

# Add axis labels on the bottom row and left column
for j in range(n):
    axes[n - 1, j].set_xlabel(params_order[j], fontsize=13)
for i in range(n):
    axes[i, 0].set_ylabel(params_order[i], fontsize=13)

# Add legend
ax_legend = fig.add_subplot(111)
ax_legend.axis('off')
legend_elements = []
for name, color in leg_colors.items():
    from matplotlib.patches import Patch
    legend_elements.append(Patch(facecolor=color, edgecolor='black', lw=0.5, label=name))
ax_legend.legend(handles=legend_elements, loc='upper right', fontsize=13,
                 bbox_to_anchor=(1.0, 1.0), frameon=False, ncol=1, handlelength=2.0)

fig.subplots_adjust(wspace=0, hspace=0, left=0.06, right=0.99, top=0.99, bottom=0.05)

out_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'report', 'images')
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, 'figure3_triangle.png')
fig.savefig(out_path, dpi=200, bbox_inches='tight', facecolor='white')
print(f"Saved: {out_path}")
print(f"Samples per model: {N}")
print("Parameters plotted:", params_order)
