"""
Simplified DELVE implementation for RPE cell cycle data.

Paper: Ranek et al., DELVE: feature selection for preserving biological
trajectories in single-cell data. Nature Communications (2024) 15:2765.

Two-step DELVE:
  Step 1: Identify dynamic co-varying feature modules via local neighborhood
          analysis (k-NN graph + local variance).
  Step 2: Rank all features by their association with the trajectory graph
          built from dynamic modules (Laplacian-style smoothness).
"""
import numpy as np
from sklearn.neighbors import NearestNeighbors
from scipy.sparse import csr_matrix


def build_knn(X, k=30, n_jobs=-1):
    """Return knn distances and indices for X."""
    nn = NearestNeighbors(n_neighbors=k, n_jobs=n_jobs).fit(X)
    dist, idx = nn.kneighbors(X)
    return dist, idx


def local_variance(X, knn_idx, k=30):
    """Per-feature local variance (mean over cells). High = dynamic."""
    Xk = X[knn_idx]                     # (n, k, d)
    var_local = Xk.var(axis=1)          # (n, d)
    return var_local.mean(axis=0)       # (d,)


def _sparse_laplacian(knn_idx, weights, n):
    """Build directed sparse Laplacian L = D - W from knn_idx and weights."""
    rows = np.repeat(np.arange(n), len(knn_idx[0]))
    cols = knn_idx.ravel()
    data = weights.ravel()
    W = csr_matrix((data, (rows, cols)), shape=(n, n))
    deg = np.asarray(W.sum(axis=1)).ravel()
    D = csr_matrix((deg, (np.arange(n), np.arange(n))), shape=(n, n))
    return D - W


def laplacian_autocorr_scores(X, knn_idx, weights):
    """Laplacian autocorrelation score per feature.
    
    score_f = <x_f, L x_f> / <x_f, x_f>
    Higher score = smoother along the k-NN graph = informative for trajectory.
    """
    n, d = X.shape
    Xf = X - X.mean(axis=0, keepdims=True)
    denom = (Xf ** 2).sum(axis=0) + 1e-8
    L = _sparse_laplacian(knn_idx, weights, n)
    LXf = Xf.T @ L @ Xf               # (d, d)
    numer = np.diag(LXf)               # (d,)
    return numer / denom


def _diverse_greedy_select(X, scores, k=30, max_corr=0.9):
    """Greedy selection: pick highest-score feature, drop correlated ones."""
    from sklearn.metrics.pairwise import cosine_similarity
    # z-score each feature so cosine is well-defined
    mu = X.mean(axis=0, keepdims=True)
    sd = X.std(axis=0, keepdims=True) + 1e-8
    Xz = (X - mu) / sd
    sim = cosine_similarity(Xz.T)          # (d, d)
    np.fill_diagonal(sim, 0)
    selected = []
    remaining = list(np.argsort(scores)[::-1])
    while len(selected) < k and remaining:
        pick = remaining.pop(0)
        selected.append(pick)
        remaining = [j for j in remaining if sim[pick, j] < max_corr]
    return np.array(selected, dtype=int)


def select_delve(X, k_dynamic=30, k_final=30, k=30, verbose=False):
    """Two-step DELVE (simplified).

    Step 1: Local neighborhood analysis.
      - Build k-NN graph on all features.
      - Compute per-feature *local variance* (variance across each cell's
        k-NN neighborhood, averaged over cells). High local variance means
        the feature varies across neighbours -> a 'dynamic' feature that
        discriminates cells along a trajectory.
      - Take top-k_dynamic local-variance features as the dynamic seed set.

    Step 2: Diversity-aware ranking of all features.
      - Score all features by local variance.
      - Greedy-select top-k_final features while dropping features whose
        cosine similarity to any already-selected feature exceeds 0.9
        (this enforces diversity across cell-cycle proteins; otherwise
        5 measurement variants of E2F1 alone would crowd out informative
        features).

    Returns:
      rank_all:         (d,) feature importance scores (higher = better)
      selected_idx:     (k_final,) indices of top features
      dynamic_seed_idx: (k_dynamic,) indices of dynamic seed features
    """
    if verbose:
        print('[DELVE] Step 1: k-NN graph on all features...')
    dist, knn_idx = build_knn(X, k=k)

    if verbose:
        print('[DELVE] Step 1: local variance...')
    lv = local_variance(X, knn_idx, k=k)

    k_dynamic = min(k_dynamic, X.shape[1])
    dynamic_seed_idx = np.argsort(lv)[::-1][:k_dynamic]
    if verbose:
        print(f'[DELVE] Step 1: dynamic seeds ({k_dynamic})')

    if verbose:
        print('[DELVE] Step 2: greedy diverse selection (max cosine sim = 0.9)...')
    selected_idx = _diverse_greedy_select(X, lv, k=k_final, max_corr=0.9)
    # Extend score array so we can also return a ranking vector.
    rank_all = lv.copy()
    return rank_all, selected_idx, dynamic_seed_idx
