"""
Plot the M33 X-7 superradiance exclusion curve, styled to match the
target_study/images/m33x7_exclusion.png reference figure.

Y-axis: P(BH not spun down | μ) — high (=1) outside resonance, low (=0) inside.
Horizontal dashed line at 0.05 = 95% CL exclusion threshold.
"""

import numpy as np
import json
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import rcParams

rcParams['font.family'] = 'DejaVu Sans'
rcParams['axes.linewidth'] = 1.0
rcParams['font.size'] = 11

workdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
results_dir = os.path.join(workdir, 'code', 'results')
img_dir = os.path.join(workdir, 'report', 'images')
os.makedirs(img_dir, exist_ok=True)

d = np.load(os.path.join(results_dir, 'curves.npz'))
mu_scan = d['mu_scan']
P_n2    = d['P_n2']
P_n6    = d['P_n6']
P_unc   = d['P_uncorr']
P_box   = d['P_box']
box_lines = d['box_lines']
M = d['M']
a = d['a']

fig, ax = plt.subplots(figsize=(6.4, 4.8), dpi=180)

# Curves
ax.plot(mu_scan, P_n2, color='#1f4e9c', lw=2.0, label='n = 2', zorder=5)
ax.plot(mu_scan, P_n6, color='#e8862a', lw=2.0, ls=':', markersize=0.001,
        marker='.', label='n $\\leq$ 6', zorder=5)
ax.plot(mu_scan, P_unc, color='#4a9e4a', lw=1.8, ls='-.', label='Uncorr.', zorder=4)

# Box reference vertical lines
for xl in box_lines:
    ax.axvline(xl, color='#c81f29', lw=1.8, ls='--', zorder=3)
ax.plot([], [], color='#c81f29', ls='--', lw=1.8, label='Box', zorder=3)

# 95% exclusion threshold
ax.axhline(0.05, color='#888888', ls='--', lw=1.2, zorder=2)
ax.text(6e-11, 0.07, '95% exclusion', ha='right', va='bottom',
        fontsize=11, color='#333333')

# Set axes
ax.set_xscale('log')
ax.set_xlim(1e-14, 1e-10)
ax.set_ylim(-0.02, 1.05)
ax.set_xticks([1e-14, 1e-13, 1e-12, 1e-11, 1e-10])
ax.set_xticklabels(['$10^{-14}$', '$10^{-13}$', '$10^{-12}$', '$10^{-11}$', '$10^{-10}$'])
ax.set_yticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
ax.set_xlabel('ULB mass $\\mu$ [eV]', fontsize=12)
ax.set_ylabel('Probability at fixed $\\mu$', fontsize=12)

# Title text (top-left inside axes)
ax.text(0.02, 0.94, 'M33 X-7', transform=ax.transAxes, fontsize=13,
        fontweight='bold', va='top', ha='left')
ax.text(0.02, 0.87, '$\\tau_{\\rm BH} = 3$ Myr', transform=ax.transAxes,
        fontsize=12, va='top', ha='left')

# Legend
ax.legend(loc='upper left', frameon=False, fontsize=11,
          bbox_to_anchor=(0.05, 0.80), ncol=1)

# Spines
ax.spines['top'].set_visible(True)
ax.spines['right'].set_visible(True)
ax.grid(False)

plt.tight_layout()
out_path = os.path.join(img_dir, 'm33x7_exclusion.png')
plt.savefig(out_path, dpi=180, bbox_inches='tight')
plt.savefig(out_path.replace('.png', '.pdf'), bbox_inches='tight')
plt.close()
print(f"Saved exclusion plot: {out_path}")

# Also save summary for report
summary_path = os.path.join(results_dir, 'summary.json')
with open(summary_path) as f:
    s = json.load(f)
print("\nSummary:")
for k, v in s.items():
    if isinstance(v, (int, float)):
        print(f"  {k}: {v}")
    else:
        print(f"  {k}: {v}")
