import numpy as np
data = np.loadtxt('data/M33_X-7_samples.dat')
M = data[:, 0]
a = data[:, 1]
print(f"N samples: {len(data)}")
print(f"M  mean = {M.mean():.3f} Msol  std = {M.std():.3f}  median = {np.median(M):.3f}  range = [{M.min():.2f}, {M.max():.2f}]")
print(f"a* mean = {a.mean():.4f}      std = {a.std():.4f}  median = {np.median(a):.4f}  range = [{a.min():.4f}, {a.max():.4f}]")

# Compute Omega_H in SI (rad/s) for each sample
G = 6.67430e-11
c = 2.99792458e8
Msun = 1.98847e30
hbar_eVs = 6.582119569e-16

M_kg = M * Msun
M_geom = G * M_kg / c**2   # meters
a_geom = a * M_geom         # meters
r_plus = M_geom + np.sqrt(M_geom**2 - a_geom**2)
# Omega_H in rad/s
Omega_H = a_geom * c / (r_plus * (r_plus + np.sqrt(r_plus**2 - a_geom**2)))
mu_res_eV = hbar_eVs * Omega_H

print(f"\nOmega_H  mean = {Omega_H.mean():.2f} rad/s   range = [{Omega_H.min():.2f}, {Omega_H.max():.2f}]")
print(f"mu_res (n=1) mean = {mu_res_eV.mean():.3e} eV   range = [{mu_res_eV.min():.3e}, {mu_res_eV.max():.3e}]")
print(f"mu_res (n=2) mean = {2*mu_res_eV.mean():.3e} eV")
print(f"mu_res (n=6) mean = {6*mu_res_eV.mean():.3e} eV")
