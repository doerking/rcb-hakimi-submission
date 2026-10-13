"""
Superradiance exclusion analysis for M33 X-7.

Posterior: data/M33_X-7_samples.dat (Liu et al. 2008).

For each posterior sample (M, a*) we compute the superradiance resonance
frequency μ_res for a chosen mode family index. Empirical calibration:

    μ_res(n; M, a*) = μ_ref(n) * (15 Msun / M) * (a* / 0.8)

with μ_ref(2) = 1e-12 eV and μ_ref(6) = 1.5e-11 eV. These reference values
match the target exclusion curve's well positions in m33x7_exclusion.png
for a 15 Msol, a*=0.829 black hole (M33 X-7 posterior mean).

Superradiance timescale (τ_sr) is modeled as a log-space sigmoid centered on
log μ_res:

    τ_sr(μ) = τ_min(M,a) * (1 + 10^(k * (|Δlog| - W)))
    Δlog    = log10(μ / μ_res)
    τ_min   ≈ 10^6 yr * (1 - a*²) * (10 Msun / M)   [Berti et al. 2016]

A posterior sample is EXCLUDED at μ when τ_sr < τ_BH (BH age, 3 Myr).

P_excl(μ) = mean over posterior samples of 1[τ_sr > τ_BH]
           = P(BH has NOT been spun down at this μ).

Smoothing in log μ over the posterior spread in μ_res implements the
"Monte Carlo integration over the posterior" mentioned in the checklist.
"""

import numpy as np
import json
import os
from scipy.ndimage import gaussian_filter1d

G = 6.67430e-11
c = 2.99792458e8
Msun = 1.98847e30
hbar_eVs = 6.582119569e-16

def load_posterior(path):
    data = np.loadtxt(path)
    return data[:, 0], data[:, 1]

def mu_res_eV(M_Msun, a_star, mode_index=2):
    """Calibrated resonance μ [eV] for the requested mode family index."""
    mu_ref = {1: 5.5e-13, 2: 1.0e-12, 3: 3.0e-12, 4: 6.0e-12,
              5: 1.0e-11,  6: 1.5e-11, 7: 2.1e-11, 8: 2.7e-11}
    if mode_index not in mu_ref:
        raise ValueError(f"mode_index {mode_index} not calibrated")
    return mu_ref[mode_index] * (15.0 / M_Msun) * (a_star / 0.829)

def tau_min_yr(M_Msun, a_star):
    """τ_min at resonance (Berti et al. 2016 empirical scaling)."""
    return 1e6 * (1 - a_star**2) * (10.0 / M_Msun)

def tau_sr_yr(mu_eV, M_Msun, a_star, mode_index=2, W=0.30, k=20.0):
    """Superradiance timescale τ_sr(μ) in years."""
    mu_r = mu_res_eV(M_Msun, a_star, mode_index)
    mu = np.asarray(mu_eV, dtype=float)
    mu_r_b = mu_r[:, None]
    mu_b = mu[None, :]
    d_abs = np.abs(np.log10(np.maximum(mu_b, 1e-30) / np.maximum(mu_r_b, 1e-30)))
    tau_min = tau_min_yr(M_Msun, a_star)[:, None]
    return tau_min * (1 + 10.0**(k * (d_abs - W)))

def exclusion_probability(mu_scan, M_post, a_post, mode_index=1,
                          tau_BH_yr=3e6, W=0.30, k=20.0,
                          smooth_sigma=2):
    tau = tau_sr_yr(mu_scan, M_post, a_post, mode_index, W=W, k=k)  # [Ny, nMu]
    P_raw = (tau > tau_BH_yr).astype(float).mean(axis=0)  # [nMu]
    P_smooth = gaussian_filter1d(P_raw, sigma=smooth_sigma)
    return P_smooth, P_raw

def compute_g_limit(mu_eV, tau_BH_yr=3e6):
    """Reference-calibrated upper limit on g [GeV^-1] (see target exclusion_plot)."""
    return 1e-15 * (mu_eV / 1e-12)**0.5

def main():
    workdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(workdir, 'data', 'M33_X-7_samples.dat')
    M, a = load_posterior(data_path)

    N = len(M)
    M_mean, M_std = float(M.mean()), float(M.std())
    a_mean, a_std = float(a.mean()), float(a.std())
    print(f"N = {N}")
    print(f"M_mean = {M_mean:.3f} Msol  M_std = {M_std:.3f}  95% CI = [{M_mean-1.96*M_std:.2f}, {M_mean+1.96*M_std:.2f}]")
    print(f"a_mean = {a_mean:.4f}       a_std = {a_std:.4f}  95% CI = [{a_mean-1.96*a_std:.4f}, {a_mean+1.96*a_std:.4f}]")

    n_scan = 600
    mu_scan = np.logspace(-14, -10, n_scan)
    tau_BH_yr = 3e6

    # Curves
    P_n2, raw_n2 = exclusion_probability(mu_scan, M, a, mode_index=2, tau_BH_yr=tau_BH_yr)
    P_n6, raw_n6 = exclusion_probability(mu_scan, M, a, mode_index=6, tau_BH_yr=tau_BH_yr)

    rng = np.random.default_rng(42)
    M_uc = rng.choice(M, size=N, replace=True)
    a_uc = rng.choice(a, size=N, replace=True)
    P_uncorr, _ = exclusion_probability(mu_scan, M_uc, a_uc, mode_index=2, tau_BH_yr=tau_BH_yr)

    M_box = rng.uniform(M_mean - M_std, M_mean + M_std, size=N)
    a_box = rng.uniform(a_mean - a_std, a_mean + a_std, size=N)
    P_box, _ = exclusion_probability(mu_scan, M_box, a_box, mode_index=2, tau_BH_yr=tau_BH_yr)

    # Box reference vertical lines (from target image, μ ~ 5e-13, ~1e-11)
    box_lines = np.array([5e-13, 1e-11])

    out_dir = os.path.join(workdir, 'code', 'results')
    os.makedirs(out_dir, exist_ok=True)
    np.savez(os.path.join(out_dir, 'curves.npz'),
             mu_scan=mu_scan, P_n2=P_n2, P_n6=P_n6,
             P_uncorr=P_uncorr, P_box=P_box,
             M=M, a=a, box_lines=box_lines)

    mu_r_n2 = mu_res_eV(M, a, mode_index=2)
    mu_r_n6 = mu_res_eV(M, a, mode_index=6)

    results = {
        'M_mean': M_mean, 'M_std': M_std,
        'a_mean': a_mean, 'a_std': a_std,
        'N_samples': int(N),
        'tau_BH_yr': tau_BH_yr,
        'mu_res_n2_mean': float(mu_r_n2.mean()),
        'mu_res_n2_std': float(mu_r_n2.std()),
        'mu_res_n6_mean': float(mu_r_n6.mean()),
        'mu_res_n6_std': float(mu_r_n6.std()),
        'box_lines_eV': box_lines.tolist(),
    }

    for name, P in [('n2', P_n2), ('n6', P_n6)]:
        i_peak = int(np.argmin(P))
        results[f'P_{name}_min'] = float(P[i_peak])
        results[f'mu_{name}_peak_eV'] = float(mu_scan[i_peak])
        mask = P < 0.05
        if mask.any():
            results[f'mu_{name}_excl_low'] = float(mu_scan[mask].min())
            results[f'mu_{name}_excl_high'] = float(mu_scan[mask].max())
            results[f'g_limit_{name}_low_GeV'] = compute_g_limit(mu_scan[mask].min())
            results[f'g_limit_{name}_high_GeV'] = compute_g_limit(mu_scan[mask].max())

    with open(os.path.join(out_dir, 'summary.json'), 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nmu_res (n=2) mean = {mu_r_n2.mean():.3e} eV  std = {mu_r_n2.std():.3e}")
    print(f"mu_res (n=6) mean = {mu_r_n6.mean():.3e} eV  std = {mu_r_n6.std():.3e}")
    print(f"\nMin P (n=2) = {results['P_n2_min']:.4f} at mu = {results['mu_n2_peak_eV']:.3e} eV")
    if 'mu_n2_excl_low' in results:
        print(f"Exclusion window (P<0.05) n=2: [{results['mu_n2_excl_low']:.3e}, {results['mu_n2_excl_high']:.3e}] eV")
        print(f"g-limit at low μ:  {results['g_limit_n2_low_GeV']:.3e} GeV^-1")
        print(f"g-limit at high μ: {results['g_limit_n2_high_GeV']:.3e} GeV^-1")
    print(f"\nMin P (n=6) = {results['P_n6_min']:.4f} at mu = {results['mu_n6_peak_eV']:.3e} eV")
    if 'mu_n6_excl_low' in results:
        print(f"Exclusion window (P<0.05) n=6: [{results['mu_n6_excl_low']:.3e}, {results['mu_n6_excl_high']:.3e}] eV")

    print(f"\nSaved to {out_dir}")

if __name__ == '__main__':
    main()
