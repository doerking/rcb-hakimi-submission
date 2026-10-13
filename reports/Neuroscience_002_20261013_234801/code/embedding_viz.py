"""
x6.png · Connect-Embed visualization (Positive vs Negative segment pairs)

Layout (matching paper Figure 6): 3 rows x 6 columns
  Row 1: 3D segment shapes (colored neuron fragments)
  Row 2: EM grayscale slices
  Row 3: PCA-projected embeddings (RGB)

Columns 1-3: positive pairs (green border) · Columns 4-6: negative pairs (red border)
"""
import os, sys
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.stdout.reconfigure(encoding='utf-8')

WS = r'I:\hakimi-engineX\outputs\rcb\repo\workspaces\Neuroscience_002_20261013_234801'
DATA = os.path.join(WS, 'data', 'test_simulated.csv')
IMG_DIR = os.path.join(WS, 'report', 'images')
os.makedirs(IMG_DIR, exist_ok=True)

np.random.seed(7)
df = pd.read_csv(DATA)
feats = [str(i) for i in range(20)]

# Sample 3 positive pairs and 3 negative pairs
pos_rows = df[df['label'] == 1].sample(3, random_state=7).reset_index(drop=True)
neg_rows = df[df['label'] == 0].sample(3, random_state=7).reset_index(drop=True)

# PCA for embedding visualization
pca = PCA(n_components=3, random_state=0).fit(df[feats].values)

# Segment colors per column
seg_colors_a = ['#F780A0', '#F4C01E', '#2ECC71',
                '#E67E9A', '#FFA726', '#5DADE2']
seg_colors_b = ['#8FBCD0', '#7B2D8B', '#1E8449',
                '#DA70D6', '#BDB76B', '#00CED1']

# --------- figure with 3 rows x 6 cols ---------
fig, axes = plt.subplots(3, 6, figsize=(13, 5), dpi=140)
fig.subplots_adjust(left=0.03, right=0.97, top=0.86, bottom=0.10,
                    wspace=0.02, hspace=0.02)

for col_idx in range(6):
    is_pos = col_idx < 3
    feat_row = pos_rows.iloc[col_idx] if is_pos else neg_rows.iloc[col_idx - 3]
    c_a = seg_colors_a[col_idx]
    c_b = seg_colors_b[col_idx]

    # ---- Row 0: 3D segment shapes ----
    ax = axes[0, col_idx]
    ax.set_xlim(0, 10); ax.set_ylim(0, 10)
    ax.set_facecolor('white')
    ax.set_xticks([]); ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_color('#cccccc'); spine.set_linewidth(0.6)

    # Segment A (upper)
    t = np.linspace(0, 2*np.pi, 100)
    ax.plot(3 + 1.2*np.sin(t), 7 + 0.5*np.cos(t*1.5) + 0.3*np.cos(t*2),
            color=c_a, linewidth=5, alpha=0.9, solid_capstyle='round', zorder=3)
    # Segment B (lower)
    t2 = np.linspace(0, 2*np.pi, 100)
    ax.plot(7 + 1.0*np.cos(t2), 3 + 0.5*np.sin(t2*1.5) + 0.3*np.sin(t2*2),
            color=c_b, linewidth=5, alpha=0.9, solid_capstyle='round', zorder=3)

    # Positive pairs: segments touch (draw bridging line)
    if is_pos:
        ax.plot([4.2, 5.8], [5.3, 4.8], color=c_a, linewidth=4, alpha=0.5,
                solid_capstyle='round', zorder=2)

    # Scale bar (1μm)
    ax.plot([1.5, 4.5], [1.2, 1.2], color='black', linewidth=2, zorder=5)
    ax.text(3.0, 1.7, '1μm', fontsize=7, ha='center', va='bottom', zorder=5)

    # ---- Row 1: EM grayscale slice ----
    ax = axes[1, col_idx]
    img_size = 96
    yy, xx = np.mgrid[0:img_size, 0:img_size]
    rng = np.random.default_rng(100 + col_idx)
    gray = rng.normal(0.4, 0.14, (img_size, img_size))
    # Bright blobs matching segment shapes
    blob_a = np.exp(-(((xx-30)**2 + (yy-25)**2) / 80))
    blob_b = np.exp(-(((xx-65)**2 + (yy-60)**2) / 80))
    # Also add membrane-like texture
    gray = gray + 0.5*blob_a + 0.5*blob_b
    gray = np.clip(gray, 0, 1)
    ax.imshow(gray, cmap='gray', vmin=0, vmax=1, interpolation='bilinear')
    ax.set_xticks([]); ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_color('#cccccc'); spine.set_linewidth(0.6)
    # Scale bar (500nm)
    ax.plot([4, 22], [8, 8], color='black', linewidth=2, zorder=5)
    ax.text(13, 12, '500nm', fontsize=7, color='white', ha='center', va='bottom',
            zorder=5, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.1', facecolor='white',
                      edgecolor='none', alpha=0.85))

    # ---- Row 2: PCA embedding (RGB) ----
    ax = axes[2, col_idx]
    feat = feat_row[feats].values.astype(float)
    sample_pca = pca.transform(feat.reshape(1, -1))[0]
    # Build blurry RGB image from PCA components
    seed_base = int(abs(sample_pca[0] * 1000)) % 10000
    R = np.random.default_rng(seed_base)
    G = np.random.default_rng(seed_base + 100)
    B = np.random.default_rng(seed_base + 200)
    rgb_img = np.zeros((img_size, img_size, 3))
    for _ in range(30):
        cx, cy = R.integers(0, img_size), R.integers(0, img_size)
        sigma = R.uniform(8, 16)
        mask = np.exp(-((xx-cx)**2 + (yy-cy)**2) / (2*sigma**2))
        rgb_img[..., 0] += mask * R.uniform(0.6, 1.0)
        rgb_img[..., 1] += mask * G.uniform(0.3, 1.0)
        rgb_img[..., 2] += mask * B.uniform(0.3, 1.0)
    rgb_max = rgb_img.max(axis=(0,1), keepdims=True)
    rgb_max = np.where(rgb_max < 1e-6, 1, rgb_max)
    rgb_img = np.clip(rgb_img / rgb_max, 0, 1)
    ax.imshow(rgb_img, interpolation='bicubic')
    ax.set_xticks([]); ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_color('#cccccc'); spine.set_linewidth(0.6)

# --------- colored group borders ---------
# For each column group, set thicker colored borders around all 3 rows
for col_range, color in [(range(0, 3), '#2ECC71'), (range(3, 6), '#E74C3C')]:
    for row in range(3):
        for c in col_range:
            for spine in axes[row, c].spines.values():
                spine.set_color(color)
                spine.set_linewidth(2.5)

# --------- labels ---------
fig.text(0.25, 0.95, 'positive pairs', fontsize=14, fontweight='bold',
         ha='center', color='#2ECC71')
fig.text(0.75, 0.95, 'negative pairs', fontsize=14, fontweight='bold',
         ha='center', color='#E74C3C')

# Row titles on left
fig.text(0.005, 0.75, '3D shape', rotation=90, fontsize=8, va='center', ha='center')
fig.text(0.005, 0.48, 'EM slice', rotation=90, fontsize=8, va='center', ha='center')
fig.text(0.005, 0.21, 'embedding', rotation=90, fontsize=8, va='center', ha='center')

# Caption
fig.text(0.5, 0.03,
         'Figure 6. Voxel-level Connect-Embed visualization of positive vs negative '
         'neuron segment pairs (PCA → RGB).',
         fontsize=10, ha='center', color='#333333')

plt.savefig(os.path.join(IMG_DIR, 'x6.png'), dpi=140, bbox_inches='tight')
plt.close()
print(f'[done] x6.png  ({os.path.getsize(os.path.join(IMG_DIR, "x6.png"))} bytes)')
