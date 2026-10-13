"""Cosmological parameters from Tables II+III of the DESI DR2 EDE paper.

Best-fit values and 1σ errors for ΛCDM, EDE, and w0wa models under
the CMB+DESI (CMB+BAO) data combination.
"""

# ΛCDM (CMB+DESI)
LCDM = {
    'omega_m': (0.3037, 0.0037),
    'H0':      (68.12, 0.28),
    'sigma8':  (0.8101, 0.0055),
    'ns':      (0.9672, 0.0034),
    'ombh2':   (0.02229, 0.00012),
    'ln10As':  (3.056,  0.014),
    'tau':     (0.0621, 0.0075),
}

# EDE (CMB+DESI)
EDE = {
    'omega_m': (0.2999, 0.0038),
    'H0':      (70.9,  1.0),
    'sigma8':  (0.8283, 0.0093),
    'f_EDE':   (0.093,  0.031),
    'log10_ac':(-3.564, 0.075),
    'ns':      (0.9817, 0.0063),
    'ombh2':   (0.02241, 0.00018),
    'ln10As':  (3.067,  0.017),
    'tau':     (0.0582, 0.0074),
}

# w0wa (CMB+DESI)
W0WA = {
    'omega_m': (0.353, 0.021),
    'H0':      (63.5,  1.9),
    'sigma8':  (0.780, 0.016),
    'w0':      (-0.42, 0.21),
    'wa':      (-1.75, 0.58),
    'ns':      (0.9632, 0.0037),
    'ombh2':   (0.02218, 0.00013),
    'ln10As':  (3.037,  0.013),
    'tau':     (0.0520, 0.0071),
}

# --- Observed data (relative deviations from the fiducial ΛCDM of the paper) ---
# DESI BAO: Δ(D_V/r_d) relative to fiducial
DESI_DVRD = [
    (0.295, -0.020, 0.010),
    (0.510, -0.015, 0.008),
    (0.700, -0.012, 0.007),
    (0.934, -0.010, 0.006),
    (1.100, -0.005, 0.007),
    (1.320,  0.000, 0.008),
    (2.330,  0.010, 0.012),
]

# DESI BAO: ΔF_AP relative to fiducial
DESI_FAP = [
    (0.295, -0.01, 0.02),
    (0.510,  0.00, 0.02),
    (0.700,  0.01, 0.02),
    (0.934,  0.02, 0.02),
    (1.100,  0.02, 0.02),
    (1.320,  0.02, 0.02),
    (2.330, -0.03, 0.04),
]

# Union3 SNe: Δμ distance modulus relative to fiducial
SNE_MU = [
    (0.1, -0.08, 0.10),
    (0.2, -0.12, 0.08),
    (0.3, -0.10, 0.07),
    (0.4, -0.07, 0.06),
    (0.5, -0.05, 0.05),
    (0.6, -0.02, 0.05),
    (0.7,  0.00, 0.05),
]
