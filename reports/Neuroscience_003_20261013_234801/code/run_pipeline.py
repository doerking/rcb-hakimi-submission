"""
Main pipeline: DELVE feature selection + PHATE embedding + metrics.

Task: Neuroscience_003 (DELVE paper reproduction on RPE cell cycle data).
Data: adata_RPE.h5ad (2759 cells x 241 features, phase G0/G1/S/G2).

Produces:
  - report/images/phate_All_features.png
  - report/images/phate_Selected.png
  - report/images/metrics_comparison.png
  - report/comparison_results.csv
  - report/selected_features.txt
  - report/selected_features_delve.txt
"""
import sys, os, time, warnings, json, argparse
sys.stdout.reconfigure(encoding='utf-8')
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import anndata as ad
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

from sklearn.neighbors import NearestNeighbors
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import normalized_mutual_info_score
from scipy.stats import kendalltau
from sklearn.cluster import KMeans

sys.path.insert(0, os.path.dirname(__file__))
from delve_simplified import select_delve

import phate

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(WORKSPACE, 'data', 'adata_RPE.h5ad')
REPORT_IMG = os.path.join(WORKSPACE, 'report', 'images')
REPORT_DIR = os.path.join(WORKSPACE, 'report')

PHASE_ORDER = ['G0', 'G1', 'S', 'G2']  # biological order (G0 arrested, then cycle)
PHASE_MAP = {p: i for i, p in enumerate(PHASE_ORDER)}

# PHATE parameters (paper-style: knn=30, transition time ~3, moderate n_pca)
PHATE_ALL_KNN = 30
PHATE_SELECTED_KNN = 30
PHATE_T = 3
PHATE_ALL_PCA = 100
PHATE_SELECTED_PCA = 30


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
def load_data():
    a = ad.read_h5ad(DATA_PATH)
    X = np.asarray(a.X).astype(np.float32)
    y = a.obs['phase'].values
    age = a.obs['annotated_age'].values.astype(float)
    state = a.obs['state'].values
    batch = a.obs['batch'].values
    print(f'[load] X shape: {X.shape}, phases: '
          f'{dict(zip(*np.unique(y, return_counts=True)))}')
    return a, X, y, age, state, batch


# ---------------------------------------------------------------------------
# PHATE embedding
# ---------------------------------------------------------------------------
def run_phate(X, knn=30, t=3, n_pca=50, random_state=42, verbose=False):
    print(f'[PHATE] knn={knn}, t={t}, n_pca={n_pca}, X shape={X.shape}')
    t0 = time.time()
    p = phate.PHATE(n_components=2, knn=knn, t=t, n_pca=n_pca,
                     random_state=random_state, verbose=False)
    z = p.fit_transform(X)
    print(f'[PHATE] done in {time.time()-t0:.1f}s, '
          f'x[{z[:,0].min():.3f},{z[:,0].max():.3f}] '
          f'y[{z[:,1].min():.3f},{z[:,1].max():.3f}]')
    return z


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------
def knn_accuracy(X_feat, y_num, k=15, n_splits=3, random_state=42):
    """k-NN classification accuracy via stratified k-fold."""
    from sklearn.model_selection import StratifiedKFold, cross_val_score
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    clf = KNeighborsClassifier(n_neighbors=k, n_jobs=-1)
    scores = cross_val_score(clf, X_feat, y_num, cv=skf, scoring='accuracy', n_jobs=-1)
    return scores.mean(), scores.std()


def phate_nmi(z, y_num, n_clusters=4, random_state=42):
    """NMI between k-means clusters on PHATE and phase labels."""
    km = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=5)
    labels = km.fit_predict(z)
    return normalized_mutual_info_score(y_num, labels)


def phate_pseudotime_corr(z, age, random_state=42):
    """Kendall tau correlation between PHATE dim1 and annotated age (pseudotime)."""
    # PHATE is orientation-free; align direction so corr is positive
    tau, _ = kendalltau(z[:, 0], age)
    return abs(tau)


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------
def plot_phate(z, y_num, title, savepath, axis_range=None):
    """Plot PHATE embedding with target-figure styling (viridis, Phase 0-3)."""
    fig, ax = plt.subplots(figsize=(5.5, 5.5))
    sc = ax.scatter(z[:, 0], z[:, 1], c=y_num, cmap='viridis',
                     s=6, edgecolors='none', vmin=0, vmax=3)
    ax.set_title(title, fontsize=11, pad=8)
    if axis_range:
        ax.set_xlim(*axis_range[0])
        ax.set_ylim(*axis_range[1])
    ax.set_xlabel('PHATE dim 1')
    ax.set_ylabel('PHATE dim 2')
    plt.colorbar(sc, ax=ax, label='Phase', pad=0.02, shrink=0.85)
    fig.tight_layout()
    fig.savefig(savepath, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f'[plot] saved {savepath}')


def plot_metrics_comparison(all_metrics, sel_metrics, savepath):
    """Side-by-side bar chart of accuracy / NMI / kendall_tau."""
    metrics = ['accuracy', 'nmi', 'kendall_tau']
    x = np.arange(len(metrics))
    w = 0.35
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    bars1 = ax.bar(x - w/2, [all_metrics[m] for m in metrics], w,
                   label='All features (baseline)', color='#4C72B0')
    bars2 = ax.bar(x + w/2, [sel_metrics[m] for m in metrics], w,
                   label='DELVE Selected (top 30)', color='#DD8452')
    ax.set_xticks(x)
    ax.set_xticklabels(metrics)
    ax.set_ylabel('Score')
    ax.set_title('RPE cell-cycle: PHATE downstream metrics\n(all features vs DELVE-selected top-30)')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    for bar in list(bars1) + list(bars2):
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, h + 0.02,
                f'{h:.3f}', ha='center', va='bottom', fontsize=9)
    fig.tight_layout()
    fig.savefig(savepath, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f'[plot] saved {savepath}')


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    os.makedirs(REPORT_IMG, exist_ok=True)
    print('=' * 60)
    print('Neuroscience_003: DELVE on RPE cell-cycle data')
    print('=' * 60)

    # 1. Load
    a, X, y, age, state, batch = load_data()
    y_num = np.array([PHASE_MAP[p] for p in y])

    # 2. Feature selection: DELVE top-30 + variance top-30 for reference
    print('\n[1/4] DELVE feature selection')
    rank_delve, sel_delve, seed_delve = select_delve(
        X, k_dynamic=30, k_final=30, k=30, verbose=True)
    top30_var = np.argsort(X.var(axis=0))[::-1][:30]
    overlap = len(set(sel_delve.tolist()) & set(top30_var.tolist()))
    print(f'[feature selection] DELVE top-30, variance top-30 overlap: {overlap}/30')

    X_sel = X[:, sel_delve]

    # 3. PHATE embeddings
    print('\n[2/4] PHATE on all features')
    z_all = run_phate(X, knn=PHATE_ALL_KNN, t=PHATE_T,
                       n_pca=PHATE_ALL_PCA, random_state=42)
    print('\n[3/4] PHATE on DELVE-selected features')
    z_sel = run_phate(X_sel, knn=PHATE_SELECTED_KNN, t=PHATE_T,
                       n_pca=PHATE_SELECTED_PCA, random_state=42)

    # 4. Metrics
    print('\n[4/4] Metrics')
    acc_all, _ = knn_accuracy(X, y_num, k=15)
    acc_sel, _ = knn_accuracy(X_sel, y_num, k=15)
    nmi_all = phate_nmi(z_all, y_num, n_clusters=4)
    nmi_sel = phate_nmi(z_sel, y_num, n_clusters=4)
    tau_all = phate_pseudotime_corr(z_all, age)
    tau_sel = phate_pseudotime_corr(z_sel, age)

    all_m = {'accuracy': acc_all, 'nmi': nmi_all, 'kendall_tau': tau_all}
    sel_m = {'accuracy': acc_sel, 'nmi': nmi_sel, 'kendall_tau': tau_sel}
    print(f'  All features : acc={acc_all:.3f} nmi={nmi_all:.3f} kendall_tau={tau_all:.3f}')
    print(f'  DELVE sel-30 : acc={acc_sel:.3f} nmi={nmi_sel:.3f} kendall_tau={tau_sel:.3f}')

    # 5. Save figures
    print('\n[saving]')
    plot_phate(z_all, y_num, 'All features (PHATE)',
               os.path.join(REPORT_IMG, 'phate_All_features.png'))
    plot_phate(z_sel, y_num, 'Selected (PHATE)',
               os.path.join(REPORT_IMG, 'phate_Selected.png'))
    plot_metrics_comparison(all_m, sel_m,
                             os.path.join(REPORT_IMG, 'metrics_comparison.png'))

    # 6. Save comparison_results.csv (matches target template)
    df = pd.DataFrame({
        'All features': [acc_all, nmi_all, tau_all],
        'Selected':     [acc_sel, nmi_sel, tau_sel],
    }, index=['accuracy', 'nmi', 'kendall_tau'])
    csv_path = os.path.join(REPORT_IMG, 'comparison_results.csv')
    df.to_csv(csv_path)
    print(f'[save] {csv_path}')

    # 7. Save selected feature lists
    with open(os.path.join(REPORT_DIR, 'selected_features_delve.txt'), 'w') as f:
        for i, idx in enumerate(sel_delve):
            f.write(f'{i+1}\t{a.var_names[idx]}\t{rank_delve[idx]:.4f}\n')
    with open(os.path.join(REPORT_DIR, 'selected_features_variance.txt'), 'w') as f:
        for i, idx in enumerate(top30_var):
            f.write(f'{i+1}\t{a.var_names[idx]}\n')

    # 8. Save PHATE embeddings for inspection
    np.savez(os.path.join(WORKSPACE, 'outputs', 'phate_embeddings.npz'),
             z_all=z_all, z_sel=z_sel, phase_labels=y)
    with open(os.path.join(WORKSPACE, 'outputs', 'selected_indices.json'), 'w') as f:
        json.dump({
            'delve_top30_idx': sel_delve.tolist(),
            'delve_top30_names': a.var_names[sel_delve].tolist(),
            'delve_seed30_idx': seed_delve.tolist(),
            'delve_seed30_names': a.var_names[seed_delve].tolist(),
            'overlap_with_variance': overlap,
        }, f, indent=2)

    # 9. Summary printout
    print('\n' + '=' * 60)
    print('DONE')
    print('=' * 60)
    print(f'All features  : accuracy={acc_all:.3f}  NMI={nmi_all:.3f}  kendall_tau={tau_all:.3f}')
    print(f'DELVE top-30  : accuracy={acc_sel:.3f}  NMI={nmi_sel:.3f}  kendall_tau={tau_sel:.3f}')
    print(f'Overlap with variance top-30: {overlap}/30')
    print(f'Selected features (top-10): {a.var_names[sel_delve[:10]].tolist()}')


if __name__ == '__main__':
    main()
