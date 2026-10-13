"""Figure 4: Gaussian Process Tg calibration with Tanimoto kernel.

Reproduces target image tanimoto_paper_style.png:
- Panel (a): Predicted vs Experimental Tg scatter with metrics
- Panel (b): Error distribution histogram
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from utils import set_style, DATA_DIR, REPORT_IMG

set_style()

# ---- Load data ----
cal_df = pd.read_csv(os.path.join(DATA_DIR, 'tg_calibration.csv'))
print(f'Calibration set: {len(cal_df)} polymers')

# ---- Load cached GP LOOCV results ----
cache_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gp_loocv_cache.npz')
d = np.load(cache_path)
y_exp = d['y_exp']
y_md = d['y_md']
y_cal = d['y_calibrated']
mae = float(d['mae'])
rmse = float(d['rmse'])
r2 = float(d['r2'])
bias = float(d['bias'])

print(f'LOOCV metrics: MAE={mae:.2f}, RMSE={rmse:.2f}, R2={r2:.3f}, Bias={bias:.2f}')
print(f'Paper target: MAE=28.07, RMSE=37.19, R2=0.848, Bias=0.23')

# ===================================================================
# Build the figure (2 panels side by side)
# ===================================================================
fig, (ax_a, ax_b) = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle('Gaussian Process Tg Calibration with Tanimoto Kernel',
            fontsize=13, fontweight='bold', y=1.0)

# ===================================================================
# Panel (a): Predicted vs Experimental
# ===================================================================
ax_a.scatter(y_exp, y_cal, c='#4A90D9', s=30, alpha=0.7,
            edgecolors='white', linewidth=0.5, label='LOOCV predictions')

# 1:1 line
min_tg = min(y_exp.min(), y_cal.min()) - 20
max_tg = max(y_exp.max(), y_cal.max()) + 20
ax_a.plot([min_tg, max_tg], [min_tg, max_tg], '--', color='#C82323', lw=1.5,
         label='1:1 line')

# Metrics annotation
metrics_text = (
    f'MAE  = {mae:.2f} K\n'
    f'RMSE = {rmse:.2f} K\n'
    f'$R^2$  = {r2:.3f}\n'
    f'Bias = {bias:.2f} K'
)
ax_a.text(0.05, 0.95, metrics_text, transform=ax_a.transAxes,
         fontsize=10, verticalalignment='top',
         bbox=dict(boxstyle='round', facecolor='#F0F5FA', edgecolor='#4A90D9', alpha=0.9),
         family='monospace')

# Paper target annotation
paper_text = (
    'Paper target (ECFP kernel):\n'
    'MAE = 28.07 K\n'
    '$R^2$ = 0.848'
)
ax_a.text(0.95, 0.55, paper_text, transform=ax_a.transAxes,
         fontsize=9, verticalalignment='top', horizontalalignment='right',
         bbox=dict(boxstyle='round', facecolor='#FFF4E0', edgecolor='#B5783A', alpha=0.9))

ax_a.set_xlabel('Experimental $T_g$ (K)', fontsize=11)
ax_a.set_ylabel('Predicted (Calibrated) $T_g$ (K)', fontsize=11)
ax_a.set_title('(a) Predicted vs Experimental', fontsize=12, fontweight='bold')
ax_a.legend(loc='lower right', fontsize=9, framealpha=0.9)
ax_a.grid(True, alpha=0.3)
ax_a.set_xlim(min_tg, max_tg)
ax_a.set_ylim(min_tg, max_tg)
ax_a.set_aspect('equal', adjustable='datalim')

# ===================================================================
# Panel (b): Error distribution
# ===================================================================
errors = y_cal - y_exp  # predicted - experimental
ax_b.hist(errors, bins=20, color='#4A90D9', edgecolor='white', alpha=0.85)

# Mean line
ax_b.axvline(0, color='#C82323', ls='--', lw=1.5, label='Zero error')
ax_b.axvline(bias, color='#2C5F87', ls=':', lw=1.5, label=f'Mean = {bias:.2f} K')

# Stats annotation
stats_text = (
    f'Mean error = {bias:.2f} K\n'
    f'Std error  = {np.std(errors):.2f} K\n'
    f'MAE        = {mae:.2f} K\n'
    f'$N$        = {len(errors)}'
)
ax_b.text(0.05, 0.95, stats_text, transform=ax_b.transAxes,
         fontsize=10, verticalalignment='top',
         bbox=dict(boxstyle='round', facecolor='#F0F5FA', edgecolor='#4A90D9', alpha=0.9),
         family='monospace')

ax_b.set_xlabel('Prediction Error (Predicted - Experimental) (K)', fontsize=11)
ax_b.set_ylabel('Count', fontsize=11)
ax_b.set_title('(b) Error Distribution', fontsize=12, fontweight='bold')
ax_b.legend(loc='upper right', fontsize=9)
ax_b.grid(True, alpha=0.3, axis='y')

# ===================================================================
# Save
# ===================================================================
os.makedirs(REPORT_IMG, exist_ok=True)
out_path = os.path.join(REPORT_IMG, 'tanimoto_paper_style.png')
fig.savefig(out_path, dpi=200, bbox_inches='tight', facecolor='white')
print(f'Saved: {out_path}')
