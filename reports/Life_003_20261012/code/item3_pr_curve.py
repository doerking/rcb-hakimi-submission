"""Life_003 code/item3_pr_curve.py — m6Anet precision-recall curves."""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import precision_recall_curve, average_precision_score
from pathlib import Path

u = pd.read_csv('outputs/rcb/repo/workspaces/Life_003_20261012/m6a_predictions_uncalled4.csv')
n = pd.read_csv('outputs/rcb/repo/workspaces/Life_003_20261012/m6a_predictions_nanopolish.csv')
l = pd.read_csv('outputs/rcb/repo/workspaces/Life_003_20261012/m6a_labels.csv')
y = l['label'].values
pu = u['probability'].values
pn = n['probability'].values

prec_u, rec_u, _ = precision_recall_curve(y, pu)
prec_n, rec_n, _ = precision_recall_curve(y, pn)
auprc_u = average_precision_score(y, pu)
auprc_n = average_precision_score(y, pn)

print(f'Uncalled4 AUPRC = {auprc_u:.3f}')
print(f'Nanopolish AUPRC = {auprc_n:.3f}')

fig, ax = plt.subplots(figsize=(8, 7))
ax.plot(rec_u, prec_u, color='#1f77b4', linewidth=2, label=f'Uncalled4 (AUPRC = {auprc_u:.3f})')
ax.plot(rec_n, prec_n, color='#ff7f0e', linewidth=2, label=f'Nanopolish (AUPRC = {auprc_n:.3f})')
ax.set_xlim(0, 1); ax.set_ylim(0, 1)
ax.set_xlabel('Recall', fontsize=12)
ax.set_ylabel('Precision', fontsize=12)
ax.set_title('Figure 4b: m6Anet Precision-Recall (HEK293T)', fontsize=13, fontweight='bold')
ax.legend(loc='lower left', fontsize=11)
ax.grid(alpha=0.3)

fig.tight_layout()
out = 'outputs/rcb/repo/workspaces/Life_003_20261012/outputs/fig4b_m6a_pr_curve.png'
fig.savefig(out, dpi=100, bbox_inches='tight', facecolor='white')
plt.close(fig)
print(f'[saved] {out} ({Path(out).stat().st_size/1024:.1f} KB)')
