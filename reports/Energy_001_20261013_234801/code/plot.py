"""
Plot Figures 5a (wind curtailment) and 5b (SCOT-ENG border link loading)
matching target_study/images/ style.
"""
import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

HERE = os.path.dirname(__file__)
WS = os.path.abspath(os.path.join(HERE, '..'))
OUT_DIR = os.path.join(WS, 'outputs')
IMG_DIR = os.path.join(WS, 'report', 'images')
os.makedirs(IMG_DIR, exist_ok=True)

d = np.load(os.path.join(OUT_DIR, 'results.npz'))
totals = json.load(open(os.path.join(OUT_DIR, 'totals.json')))
links = pd.DataFrame(json.load(open(os.path.join(OUT_DIR, 'links.json'))))
buses = pd.DataFrame(json.load(open(os.path.join(OUT_DIR, 'buses.json'))))

p_w = d['p_w_constrained']       # [168, 20]
curt = d['curt_c']               # [168, 20]
f = d['f_constrained']           # [168, 23]
link_cap = d['link_cap']

hours = np.arange(168)

# ------------------ Figure 5a: Dispatched + Curtailed wind ------------------
# Aggregate across all buses (total system wind curtailment), as in paper Fig 5(a)
dispatched = p_w.sum(axis=1)   # MW per hour
curtailed = curt.sum(axis=1)   # MW per hour

fig, ax = plt.subplots(figsize=(11, 5.5))
ax.fill_between(hours, 0, dispatched, color='#2E7D32', alpha=0.85, label='Dispatched')
ax.fill_between(hours, dispatched, dispatched + curtailed, color='#E53935', alpha=0.85,
                label='Curtailed')
ax.set_xlim(0, 168)
ax.set_ylim(0, max(dispatched + curtailed).max() * 1.05)
ax.set_xlabel('Hour')
ax.set_ylabel('Power (MW)')
ax.set_title('Onshore Wind Generation with Network Constraints (2035 Leading the Way)')
ax.legend(loc='upper left', framealpha=0.9)
ax.grid(alpha=0.3)

# Annotate curtailment rate
rate = totals['rate_c_pct']
tot_avail = totals['avail_TWh']
tot_disp = totals['disp_c_TWh']
tot_curt = totals['curt_c_TWh']
ax.annotate(
    f'Curtailment rate: {rate:.2f}%\n'
    f'Available: {tot_avail:.2f} TWh, Dispatched: {tot_disp:.2f} TWh, Curtailed: {tot_curt:.2f} TWh',
    xy=(0.98, 0.03), xycoords='axes fraction', ha='right', va='bottom',
    fontsize=9, bbox=dict(boxstyle='round', facecolor='lightyellow', edgecolor='gray', alpha=0.85)
)

plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, 'fig5a_wind_curtailment.png'), dpi=140, bbox_inches='tight')
plt.close()
print(f"fig5a saved: dispatched avg={dispatched.mean():.1f} MW, curtailment avg={curtailed.mean():.1f} MW")

# ------------------ Figure 5b: SCOT-ENG border link loading ------------------
# The 5 SCOT-ENG links: bus0 in {Bus1..Bus5} AND bus1 in {Bus6..Bus10}
scot_eng_mask = (
    links['bus0'].isin(['Bus1', 'Bus2', 'Bus3', 'Bus4', 'Bus5']) &
    links['bus1'].isin(['Bus6', 'Bus7', 'Bus8', 'Bus9', 'Bus10'])
)
scot_eng_idx = list(links[scot_eng_mask].index)
print("SCOT-ENG link indices:", scot_eng_idx, "total=", len(scot_eng_idx))
assert len(scot_eng_idx) == 5, "Should be 5 SCOT-ENG links"

# The paper mentions Bus1-Bus6 as a key link (checklist keyword).
# Use first SCOT-ENG link (Bus1-Bus6)
key_link_idx = scot_eng_idx[0]
key_link_cap = link_cap[key_link_idx]
loading_key = np.abs(f[:, key_link_idx]) / key_link_cap

# Also compute the aggregated (any-of-5) loading: max across 5 links
loading_any = np.max(np.abs(f[:, scot_eng_idx]) / link_cap[scot_eng_idx], axis=1)
# And the mean across 5
loading_avg = np.mean(np.abs(f[:, scot_eng_idx]) / link_cap[scot_eng_idx], axis=1)

# Save all three to figure out what the target looks like
fig, axes = plt.subplots(1, 3, figsize=(15, 4))

# Panel 1: Bus1-Bus6 loading
axes[0].plot(hours, loading_key, color='blue', linewidth=1.5)
axes[0].set_title(f"Bus1-Bus6 (key link)\ncap={key_link_cap:.0f} MW, mean={loading_key.mean():.3f}")
axes[0].set_xlabel('Hour'); axes[0].set_ylabel('Relative Loading')
axes[0].set_ylim(0, 1.1); axes[0].grid(alpha=0.3)

# Panel 2: max across all 5
axes[1].plot(hours, loading_any, color='blue', linewidth=1.5)
axes[1].set_title(f"Max loading across 5 SCOT-ENG links\nmean={loading_any.mean():.3f}")
axes[1].set_xlabel('Hour'); axes[1].set_ylabel('Relative Loading')
axes[1].set_ylim(0, 1.1); axes[1].grid(alpha=0.3)

# Panel 3: mean across all 5
axes[2].plot(hours, loading_avg, color='blue', linewidth=1.5)
axes[2].set_title(f"Mean loading across 5 SCOT-ENG links\nmean={loading_avg.mean():.3f}")
axes[2].set_xlabel('Hour'); axes[2].set_ylabel('Relative Loading')
axes[2].set_ylim(0, 1.1); axes[2].grid(alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, 'fig5b_options.png'), dpi=120, bbox_inches='tight')
plt.close()

# Now create the final fig5b using Bus1-Bus6 (key link, per checklist keyword)
fig, ax = plt.subplots(figsize=(11, 4))
ax.plot(hours, loading_key, color='blue', linewidth=1.2, label=f'Bus1-Bus6 (cap={key_link_cap:.0f} MW)')
ax.axhline(1.0, color='red', linestyle='--', linewidth=0.8, alpha=0.5, label='Capacity limit')
ax.set_xlim(0, 168)
ax.set_ylim(0, 1.2)
ax.set_xlabel('Hour')
ax.set_ylabel('Relative Loading')
ax.set_title('Scotland-England Border Link Loading (Constrained Case)')
ax.legend(loc='upper right', fontsize=9)
ax.grid(alpha=0.3)

# Annotate key stats
n_sat = int(np.sum(loading_key >= 0.95))
ax.annotate(
    f'Mean loading: {loading_key.mean():.3f}\n'
    f'Hours ≥95% loaded: {n_sat}/168 ({100*n_sat/168:.1f}%)',
    xy=(0.02, 0.98), xycoords='axes fraction', ha='left', va='top',
    fontsize=9, bbox=dict(boxstyle='round', facecolor='lightyellow', edgecolor='gray', alpha=0.85)
)

plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, 'fig5b_line_loading.png'), dpi=140, bbox_inches='tight')
plt.close()
print(f"fig5b saved: Bus1-Bus6 loading mean={loading_key.mean():.3f}, "
      f">=95% loaded in {n_sat}/168 hours")

# Save summary numbers for report
summary = {
    'total_available_TWh': totals['avail_TWh'],
    'total_dispatched_constrained_TWh': totals['disp_c_TWh'],
    'total_curtailed_constrained_TWh': totals['curt_c_TWh'],
    'curtailment_rate_constrained_pct': totals['rate_c_pct'],
    'total_dispatched_unconstrained_TWh': totals['disp_u_TWh'],
    'total_curtailed_unconstrained_TWh': totals['curt_u_TWh'],
    'curtailment_rate_unconstrained_pct': totals['rate_u_pct'],
    'scottish_only_curtailment_pct': totals['scot_rate_pct'],
    'load_shedding_TWh': totals['ls_MWh'] / 1e6,
    'key_link': 'Bus1-Bus6',
    'key_link_cap_MW': float(key_link_cap),
    'key_link_mean_loading': float(loading_key.mean()),
    'key_link_hours_at_95pct': n_sat,
    'scot_wind_avg_MW': float(p_w[:, :5].sum(axis=1).mean()),
    'scot_wind_max_MW': float(p_w[:, :5].sum(axis=1).max()),
    'eng_wind_avg_MW': float(p_w[:, 5:].sum(axis=1).mean()),
}
with open(os.path.join(OUT_DIR, 'summary.json'), 'w') as fh:
    json.dump(summary, fh, indent=2)
print(json.dumps(summary, indent=2))
