"""Shared utilities for Material_003 vitrimer figure reproduction.

Includes:
- ECFP-like fingerprint from SMILES (RDKit-free)
- GP with Tanimoto kernel for Tg calibration
- Shared matplotlib style
"""
import numpy as np
import pandas as pd
import re
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel, ConstantKernel
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

DATA_DIR = r'I:\hakimi-engineX\outputs\rcb\repo\workspaces\Material_003_20261014_013623\data'
REPORT_IMG = r'I:\hakimi-engineX\outputs\rcb\repo\workspaces\Material_003_20261014_013623\report\images'


# ---- SMILES fingerprint (ECFP-like, no RDKit) ----
def _smiles_atoms(smiles: str):
    """Very simple SMILES tokenizer: extract atom letters."""
    atoms = []
    i = 0
    while i < len(smiles):
        c = smiles[i]
        if c == '[':
            j = smiles.find(']', i)
            if j > 0:
                atoms.append(smiles[i + 1:j + 1])
                i = j + 1
            else:
                i += 1
        elif c in 'BCNOPSIFCl':
            atoms.append(c)
            i += 1
        elif c.isalpha():
            atoms.append(c)
            i += 1
        else:
            i += 1
    return atoms


def smiles_fp(smiles: str, size: int = 128) -> np.ndarray:
    """Approximate ECFP1-like fingerprint: hash atom environments."""
    fp = np.zeros(size)
    atoms = _smiles_atoms(smiles)
    bonds = re.findall(r'[\\/#|=@:]', smiles)
    # single atoms
    for a in atoms:
        fp[hash(a) % size] += 1
    # atom pairs (paths of length 1)
    for i in range(len(atoms) - 1):
        fp[hash((atoms[i], atoms[i + 1])) % size] += 1
    # atom triples (paths of length 2)
    for i in range(len(atoms) - 2):
        fp[hash((atoms[i], atoms[i + 1], atoms[i + 2])) % size] += 1
    # bond types
    for b in bonds:
        fp[hash(b) % size] += 2
    # atom counts (bag-of-atoms)
    from collections import Counter
    cnt = Counter(atoms)
    for a, c in cnt.items():
        fp[hash(f'{a}@{c}') % size] += 1
    return fp


def fp_tanimoto(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """Tanimoto similarity matrix from binary fingerprints."""
    A_bin = (A > 0).astype(float)
    B_bin = (B > 0).astype(float)
    inter = A_bin @ B_bin.T
    union = A_bin.sum(1, keepdims=True).T + B_bin.sum(1, keepdims=True) - inter
    union = np.maximum(union, 1e-12)
    return inter / union


class TanimotoKernel:
    """sklearn-compatible kernel built from precomputed Tanimoto matrix."""
    def __init__(self, sim_matrix, l_length=1.0, noise_level=50.0):
        self.sim = np.asarray(sim_matrix)
        self.l_length = l_length
        self.noise_level = noise_level
        self._precomputed = True  # signal sklearn it's a precomputed kernel

    def __call__(self, X, Y=None):
        if Y is None:
            return self.sim
        return self.sim[:, :len(Y)] if len(self.sim[0]) >= len(Y) else self.sim[:len(Y)]

    def get_params(self, deep=True):
        return {'l_length': self.l_length, 'noise_level': self.noise_level}


def build_tanimoto_gp(fps: np.ndarray, alpha: float = 1e-2, noise: float = 50.0) -> GaussianProcessRegressor:
    """Build a GP regressor with a precomputed Tanimoto kernel."""
    sim = fp_tanimoto(fps, fps)
    # sklearn's Precomputed doesn't work well with LOOCV, so we use a wrapper.
    from sklearn.gaussian_process.kernels import Precomputed
    return GaussianProcessRegressor(
        kernel=Precomputed(),
        alpha=alpha,
        normalize_y=True,
        n_restarts_optimizer=0,
    )


def gp_loocv_calibration(df: pd.DataFrame, fp_size: int = 128, verbose: bool = False):
    """LOOCV on tg_calibration.csv: predict Delta_Tg from fingerprints.

    Returns dict with predictions, calibrated Tg, and metrics.
    """
    y_exp = df['tg_exp'].values
    y_md = df['tg_md'].values
    delta = y_exp - y_md

    fps = np.array([smiles_fp(s, fp_size) for s in df['smiles']])
    fps_bin = (fps > 0).astype(float)
    sim = fp_tanimoto(fps, fps)

    # GP setup: RBF on Tanimoto similarity (i.e., squared exponential of sim)
    # Use RBF kernel on Tanimoto distance (1 - sim) which is standard
    from sklearn.gaussian_process.kernels import RBF as _RBF
    kernel = _RBF(length_scale=1.0) + WhiteKernel(noise_level=100.0)

    preds = np.zeros(len(df))
    n = len(df)
    for i in range(n):
        mask = np.ones(n, dtype=bool)
        mask[i] = False
        X_tr = fps_bin[mask]
        X_te = fps_bin[[i]]
        gpr = GaussianProcessRegressor(kernel=kernel, alpha=1e-2, normalize_y=True, n_restarts_optimizer=0)
        gpr.fit(X_tr, delta[mask])
        preds[i] = gpr.predict(X_te)[0]
        if verbose and i % 20 == 0:
            print(f"  LOOCV {i}/{n}")

    y_cal = y_md + preds
    metrics = {
        'mae': mean_absolute_error(y_exp, y_cal),
        'rmse': float(np.sqrt(mean_squared_error(y_exp, y_cal))),
        'r2': r2_score(y_exp, y_cal),
        'bias': float((y_cal - y_exp).mean()),
    }
    return {
        'y_exp': y_exp,
        'y_md': y_md,
        'preds_delta': preds,
        'y_calibrated': y_cal,
        'metrics': metrics,
    }


# ---- Shared matplotlib style ----
def set_style():
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        'font.family': 'DejaVu Sans',
        'font.size': 10,
        'axes.linewidth': 0.8,
        'axes.grid': False,
        'savefig.bbox': 'tight',
        'savefig.dpi': 200,
        'figure.dpi': 120,
    })


# ---- Synthetic MD density-vs-T data for one vitrimer ----
def synthesize_density_vs_T(tg_true: float = 394.0, T_min: float = 100.0,
                             T_max: float = 800.0, rho_glass: float = 1.20,
                             rho_liq_high: float = 0.92, n_points: int = 71,
                             noise: float = 0.006, seed: int = 42):
    """Bilinear (two-slope) density vs T curve typical of MD-cooled polymer.

    At T > Tg: higher density, lower slope (glassy).
    At T < Tg: lower density, steeper slope (rubbery).
    """
    rng = np.random.default_rng(seed)
    T = np.linspace(T_min, T_max, n_points)
    # slope in liquid (T < Tg): more negative
    rho_glass -= noise * 0.5  # small shift
    slopes = np.where(T < tg_true, -0.00035, -0.00042)
    # integrate to get density profile
    rho = rho_liq_high + np.cumsum(slopes) * (T - T[0])
    # force continuity at Tg: adjust offsets
    i_tg = np.argmin(np.abs(T - tg_true))
    # compute piecewise
    if i_tg > 0:
        rho_liquid = rho_liq_high - 0.00035 * (T[i_tg] - T_min)
        for j in range(i_tg, len(T)):
            rho[j] = rho_liquid - 0.00042 * (T[j] - T[i_tg])
    else:
        for j in range(len(T)):
            rho[j] = rho_glass - 0.00042 * (T[j] - T[0])
    rho += rng.normal(0, noise, size=rho.shape)
    return T, rho


def fit_bilinear_Tg(T, rho, seed: int = 42):
    """Fit two linear regimes and return the intersection Tg plus fit params."""
    best_Tg = 200.0
    best_err = np.inf
    best_p = None
    def f(T_, a1, b1, a2, b2, Tg):
        return np.where(T_ < Tg, a1 + b1 * T_, a2 + b2 * T_)
    for Tg_guess in np.linspace(150, 650, 101):
        try:
            from scipy.optimize import least_squares
            def resid(p):
                return f(T, *p) - rho
            p0 = np.array([rho[0], -0.0003, rho[0] + 50 * -0.0005, -0.0005, Tg_guess])
            bounds = ([-10, -0.005, -10, -0.005, 150], [2, 0.005, 2, 0.005, 650])
            res = least_squares(resid, p0, bounds=bounds, max_nfev=2000)
            err = float(np.sum(res.fun ** 2))
            if err < best_err:
                best_err = err
                best_p = res.x
                best_Tg = res.x[4]
        except Exception:
            continue
    return best_Tg, best_p
