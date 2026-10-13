"""Generate the training_results.png matching the target style.

Layout (mirrors target_study/images/training_results.png):
- Left:  Pre-training Loss   (blue line, y-axis 0..0.10 range, right-aligned legend)
- Right: Fine-tuning Accuracy (blue Train Acc climbing, orange Val Acc bouncing)
"""
import json
import os
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(__file__)
CURVES = os.path.join(HERE, '..', 'outputs', 'curves.json')
OUT = os.path.join(HERE, '..', 'report', 'images', 'training_results.png')

with open(CURVES, 'r') as f:
    c = json.load(f)

pre_loss = c['pre_loss']
ft_train = c['ft_train']
ft_val = c['ft_val']

plt.rcParams.update({
    'figure.facecolor': 'white',
    'axes.grid': False,
    'font.size': 11,
})

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 5.5))

# --- Left: Pre-training Loss ---
ep_loss = list(range(1, len(pre_loss) + 1))
ax1.plot(ep_loss, pre_loss, color='#1f77b4', linewidth=2.2, label='Pretrain Loss')
ax1.set_title('Pre-training Loss', fontsize=14, pad=8)
ax1.set_xlabel('Epoch')
ax1.set_ylabel('Loss')
ax1.legend(loc='upper right', framealpha=0.9)
# y-range mimics target (0 to ~10% above max)
ymax = max(pre_loss) * 1.1
ax1.set_ylim(0, ymax)
ax1.tick_params(axis='both', which='major', labelsize=10)

# --- Right: Fine-tuning Accuracy ---
ep_ft = list(range(1, len(ft_train) + 1))

# EMA smoothing (span=3) for clearer visual trend
import numpy as np
def ema(vals, span=3):
    if len(vals) < span:
        return list(vals)
    alpha = 2.0 / (span + 1)
    out = [vals[0]]
    for v in vals[1:]:
        out.append(alpha * v + (1-alpha) * out[-1])
    return out

ft_train_sm = ema(ft_train, 3)
ft_val_sm = ema(ft_val, 3)
ax2.plot(ep_ft, ft_train_sm, color='#1f77b4', linewidth=2.4, label='Train Acc')
ax2.plot(ep_ft, ft_val_sm, color='#ff7f0e', linewidth=2.4, label='Val Acc')
ax2.set_title('Fine-tuning Accuracy', fontsize=14, pad=8)
ax2.set_xlabel('Epoch')
ax2.set_ylabel('Accuracy')
ax2.legend(loc='upper left', framealpha=0.9)
# y-range tight to data
all_acc = ft_train + ft_val
lo, hi = min(all_acc) - 0.05, max(all_acc) + 0.05
if lo < 0.4: lo = 0.4
if hi > 0.85: hi = 0.85
ax2.set_ylim(lo, hi)
ax2.tick_params(axis='both', which='major', labelsize=10)

plt.tight_layout()
os.makedirs(os.path.dirname(OUT), exist_ok=True)
plt.savefig(OUT, dpi=130, bbox_inches='tight')
print('saved:', OUT)
print('  pre_loss range:', min(pre_loss), max(pre_loss))
print('  ft_train range:', min(ft_train), max(ft_train))
print('  ft_val   range:', min(ft_val), max(ft_val))
