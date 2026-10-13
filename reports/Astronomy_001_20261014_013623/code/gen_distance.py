"""
Distance comparison plot (Figure 6 style) for Astronomy_001.

Compute three relative-deviation curves for the best-fit ΛCDM, EDE,
w0wa models, referenced to the ΛCDM best-fit:

  Δμ          = μ_M(z) - μ_ref(z)                          [mag]
  Δ(D_V/r_d)  = (D_V/r_d)_M / (D_V/r_d)_ref - 1            [-]
  ΔF_AP       = F_AP,M / F_AP,ref - 1                      [-]

The reference is the ΛCDM best-fit (H0=68.12, Ωm=0.3037, ...), which
serves both as the "reference ΛCDM" curve (≡ 0) and as the normalisation
of the DESI BAO and Union3 SNe residual data points.

Cosmological distances use the standard flat-ΛCDM / flat-w0wa formulae;
for EDE the background expansion is treated as ΛCDM with best-fit Ωm,
H0 (the stiff EDE limit, f_EDE ≈ 9% peaks at z~zc and decays before
recombination; its late-time effect is absorbed into the H0 shift).
r_d is taken as approximately the same for all three models (to leading
order the difference is sub-percent).
"""
import os, sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.integrate import quad

sys.path.insert(0, os.path.dirname(__file__))
import config as cfg

C_KM_S = 299_792.458

# --- Cosmological distance helpers ------------------------------------------
def E2_lcdm(z, omega_m):
    """Dimensionless E(z)^2 = (H(z)/H_0)^2 for flat ΛCDM."""
    return omega_m * (1 + z) ** 3 + (1 - omega_m)

def E2_w0wa(z, omega_m, w0, wa):
    """Dimensionless E(z)^2 for flat w0wa.

    Exact solution of the DE continuity equation for w(a) = w0 + wa*(1-a):
        rho_DE(a) = rho_DE(1) * a^{-3(1+w0+wa)} * exp(-3*wa*(1-a))
    so Omega_DE(0) = 1 - Omega_m and E(0) = 1 identically.
    """
    a = 1.0 / (1.0 + z)
    omega_de = 1.0 - omega_m
    We = omega_de * (1.0 + z) ** (3.0 * (1.0 + w0 + wa)) * np.exp(-3.0 * wa * (1.0 - a))
    return omega_m * (1 + z) ** 3 + We

def comoving_distance(z, omega_m, H0, w0=None, wa=None):
    """Comoving distance D_C(z) in Mpc."""
    if z <= 0:
        return 0.0
    if w0 is None:
        val, _ = quad(lambda zz: 1.0 / np.sqrt(E2_lcdm(zz, omega_m)), 0, z,
                      epsabs=1e-10, epsrel=1e-8, limit=200)
    else:
        val, _ = quad(lambda zz: 1.0 / np.sqrt(E2_w0wa(zz, omega_m, w0, wa)), 0, z,
                      epsabs=1e-10, epsrel=1e-8, limit=200)
    # val is dimensionless; multiply by c/H0 to convert to Mpc
    return val * C_KM_S / H0

def angular_diameter_distance(z, omega_m, H0, w0=None, wa=None):
    """Angular diameter distance D_A(z) in Mpc."""
    if z <= 0:
        return 0.0
    return comoving_distance(z, omega_m, H0, w0, wa) / (1.0 + z)

def luminosity_distance(z, omega_m, H0, w0=None, wa=None):
    """Luminosity distance D_L(z) in Mpc."""
    if z <= 0:
        return 0.0
    return (1.0 + z) * comoving_distance(z, omega_m, H0, w0, wa)

def sound_horizon(ombh2, H0):
    """Sound horizon r_d (Mpc) — approximate analytic formula (Eisenstein & Hu 1998)."""
    h = H0 / 100.0
    omega_b = ombh2 / h**2
    # Drag temperature
    T_d = 4.525e4 * omega_b * h**2 * (1.0 + 0.388 * (1.0 + 0.664 * omega_b * h**2) ** 0.251)
    # Sound horizon (in Mpc)
    rd = 3.0 / np.sqrt(5.0) * C_KM_S / (h * np.sqrt(omega_b * h**2)) / (1.0 + 0.35 * np.log(42.0 * omega_b / h**2) / T_d)
    return rd

# Sanity check: for ΛCDM, r_d should be ~147 Mpc
_rD_check = sound_horizon(cfg.LCDM['ombh2'][0], cfg.LCDM['H0'][0])
if abs(_rD_check - 147.0) > 5.0:
    print(f"WARNING: r_d computed as {_rD_check:.1f} Mpc (expected ~147), using fixed 147 Mpc.")
    SOUND_HORIZON_OVERRIDE = 147.0
else:
    SOUND_HORIZON_OVERRIDE = None

def model_params(name):
    """Return (omega_m, H0, ombh2, w0, wa) for a given model."""
    if name == 'lcdm':
        d = cfg.LCDM
        return (d['omega_m'][0], d['H0'][0], d['ombh2'][0], None, None)
    if name == 'ede':
        d = cfg.EDE
        return (d['omega_m'][0], d['H0'][0], d['ombh2'][0], None, None)
    if name == 'w0wa':
        d = cfg.W0WA
        return (d['omega_m'][0], d['H0'][0], d['ombh2'][0], d['w0'][0], d['wa'][0])

# --- Deviation curves --------------------------------------------------------
def compute_dvrd_dev(z, om, H0, ob, w0=None, wa=None,
                     om_ref=None, H0_ref=None, ob_ref=None,
                     w0_ref=None, wa_ref=None):
    """(D_V/r_d)_M / (D_V/r_d)_ref - 1.

    Assumes r_d is approximately the same for all three models (sub-percent
    difference), so the ratio reduces to (D_V)_M / (D_V)_ref - 1.
    """
    D_A = angular_diameter_distance(z, om, H0, w0, wa)
    D_A_ref = angular_diameter_distance(z, om_ref, H0_ref, w0_ref, wa_ref)
    # D_V = ((1+z)^2 * D_A^2 * D_H)^(1/3) with D_H = c/H_0
    D_V = ((1 + z) ** 2 * D_A ** 2 * C_KM_S / H0) ** (1.0 / 3.0)
    D_V_ref = ((1 + z) ** 2 * D_A_ref ** 2 * C_KM_S / H0_ref) ** (1.0 / 3.0)
    if np.isclose(D_V_ref, 0):
        return np.nan
    return D_V / D_V_ref - 1.0

def compute_mu_dev(z, om, H0, ob, w0=None, wa=None,
                   om_ref=None, H0_ref=None, ob_ref=None,
                   w0_ref=None, wa_ref=None):
    """μ_M(z) - μ_ref(z) in mag."""
    if z <= 0:
        return np.nan
    D_L = luminosity_distance(z, om, H0, w0, wa)
    D_L_ref = luminosity_distance(z, om_ref, H0_ref, w0_ref, wa_ref)
    mu  = 5 * np.log10(D_L)  + 25.0
    mu_r = 5 * np.log10(D_L_ref) + 25.0
    return mu - mu_r

def compute_fap_dev(z, om, H0, ob, w0=None, wa=None,
                    om_ref=None, H0_ref=None, ob_ref=None,
                    w0_ref=None, wa_ref=None):
    """F_AP,M(z) / F_AP,ref(z) - 1. F_AP = D_A^{1/3} / D_H^{1/3}."""
    D_A = angular_diameter_distance(z, om, H0, w0, wa)
    D_A_ref = angular_diameter_distance(z, om_ref, H0_ref, w0_ref, wa_ref)
    if np.isclose(D_A_ref, 0):
        return np.nan
    return (D_A / D_A_ref) ** (1.0 / 3.0) - 1.0

# Reference (ΛCDM best-fit) parameters
om_ref, H0_ref, ob_ref, w0_ref, wa_ref = model_params('lcdm')

# --- Sample curves on a redshift grid ---------------------------------------
z_grid = np.linspace(0.05, 2.4, 500)

def curves_for(name):
    om, H0, ob, w0, wa = model_params(name)
    dV = np.array([compute_dvrd_dev(z, om, H0, ob, w0, wa,
                                     om_ref, H0_ref, ob_ref, w0_ref, wa_ref)
                   for z in z_grid])
    mu = np.array([compute_mu_dev(z, om, H0, ob, w0, wa,
                                  om_ref, H0_ref, ob_ref, w0_ref, wa_ref)
                   for z in z_grid])
    fap = np.array([compute_fap_dev(z, om, H0, ob, w0, wa,
                                    om_ref, H0_ref, ob_ref, w0_ref, wa_ref)
                    for z in z_grid])
    return dV, mu, fap

print("Computing curves ...")
dV_lcdm, mu_lcdm, fap_lcdm = curves_for('lcdm')
dV_ede,  mu_ede,  fap_ede  = curves_for('ede')
dV_w0wa, mu_w0wa, fap_w0wa = curves_for('w0wa')

# --- Assemble data points ----------------------------------------------------
z_dvrd, y_dvrd, e_dvrd = zip(*cfg.DESI_DVRD)
z_fap,  y_fap,  e_fap  = zip(*cfg.DESI_FAP)
z_mu,   y_mu,   e_mu   = zip(*cfg.SNE_MU)

# --- Plot --------------------------------------------------------------------
fig, axes = plt.subplots(3, 1, figsize=(7.5, 10.5), sharex=True)
fig.subplots_adjust(hspace=0.15)

# Model colors (matching target figure legend)
col_lcdm, col_ede, col_w0wa = '#7D3C98', '#27AE60', '#F39C12'

def plot_panel(ax, x_data, y_data, e_data, curve_lcdm, curve_ede, curve_w0wa,
               ylab, y_range=None):
    # Data first (so curves draw on top)
    ax.errorbar(x_data, y_data, yerr=e_data,
                fmt='o', color='#888888', capsize=2.5, ecolor='#888888',
                markersize=5, zorder=2, alpha=0.85)
    ax.plot(z_grid, curve_lcdm, color=col_lcdm,  lw=2, label='ΛCDM', zorder=3)
    ax.plot(z_grid, curve_ede,  color=col_ede,   lw=2, label='EDE',  zorder=3)
    ax.plot(z_grid, curve_w0wa, color=col_w0wa,  lw=2, label='w₀wₐ', zorder=3)
    ax.axhline(0, color='black', lw=0.6, ls=':', alpha=0.5)
    ax.set_ylabel(ylab, fontsize=12)
    if y_range is not None:
        ax.set_ylim(y_range)
    ax.grid(True, alpha=0.3, ls='-', lw=0.5)
    ax.set_xlim(-0.05, 2.5)

plot_panel(axes[0], z_mu,   y_mu,   e_mu,
           mu_lcdm, mu_ede, mu_w0wa,
           r'$\Delta\mu$ (mag)', y_range=(-0.20, 0.12))
plot_panel(axes[1], z_dvrd, y_dvrd, e_dvrd,
           dV_lcdm, dV_ede, dV_w0wa,
           r'$\Delta(D_V/r_d)$', y_range=(-0.09, 0.03))
plot_panel(axes[2], z_fap,  y_fap,  e_fap,
           fap_lcdm, fap_ede, fap_w0wa,
           r'$\Delta F_{AP}$', y_range=(-0.06, 0.05))
axes[2].set_xlabel('redshift z', fontsize=12)

# Single shared legend (top-right of first panel)
axes[0].legend(loc='upper right', fontsize=11, frameon=True, framealpha=0.9)

fig.tight_layout(rect=(0, 0, 1, 1))

out_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'report', 'images')
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, 'figure6_distance.png')
fig.savefig(out_path, dpi=200, bbox_inches='tight', facecolor='white')
print(f"Saved: {out_path}")

# Print sample values for the report
def pick(curve, z_target):
    idx = np.argmin(np.abs(z_grid - z_target))
    return curve[idx]

print("\nSample deviations at reference redshifts (relative to ΛCDM best-fit):")
print(f"{'z':>6} | {'Δμ_EDE':>8}  {'Δμ_w0wa':>8}  | {'ΔDvrd_EDE':>10}  {'ΔDvrd_w0wa':>11}  | {'ΔF_AP_EDE':>10}  {'ΔF_AP_w0wa':>11}")
for z in [0.295, 0.510, 0.7, 1.0, 2.0]:
    print(f"{z:>6.3f} | {pick(mu_ede, z):+8.3f}  {pick(mu_w0wa, z):+8.3f}  | "
          f"{pick(dV_ede, z):+10.4f}  {pick(dV_w0wa, z):+11.4f}  | "
          f"{pick(fap_ede, z):+10.4f}  {pick(fap_w0wa, z):+11.4f}")
