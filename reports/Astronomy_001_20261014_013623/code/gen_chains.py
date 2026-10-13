"""
Generate simulated MCMC chains (item 1 of the checklist).

For each of ΛCDM, EDE, and w0wa, draw 20,000 Gaussian samples centred on the
best-fit values and 1σ errors reported in Tables II+III of the DESI DR2 EDE
paper (CMB+DESI data combination).

Output: report/chains/<MODEL>.chains.npz  with keys = parameter names.
        report/chains/<MODEL>.chains.getdist  (plain text; header row of
        parameter names, followed by N samples — column order matches the
        numpy array shape; the format is compatible with GetDist's
        `getdist.load_chain`).
"""
import os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
import config as cfg

RNG_SEED = 20261014
N = 20000

# Parameter order for each model (kept consistent for triangle + GetDist)
MODEL_PARAMS = {
    'lcdm': {
        'omega_m':      cfg.LCDM['omega_m'],
        'H0':           cfg.LCDM['H0'],
        'sigma8':       cfg.LCDM['sigma8'],
        'ns':           cfg.LCDM['ns'],
        'ombh2':        cfg.LCDM['ombh2'],
        'ln10As':       cfg.LCDM['ln10As'],
        'tau':          cfg.LCDM['tau'],
    },
    'ede': {
        'omega_m':      cfg.EDE['omega_m'],
        'H0':           cfg.EDE['H0'],
        'sigma8':       cfg.EDE['sigma8'],
        'f_EDE':        cfg.EDE['f_EDE'],
        'log10_ac':     cfg.EDE['log10_ac'],
        'ns':           cfg.EDE['ns'],
        'ombh2':        cfg.EDE['ombh2'],
        'ln10As':       cfg.EDE['ln10As'],
        'tau':          cfg.EDE['tau'],
    },
    'w0wa': {
        'omega_m':      cfg.W0WA['omega_m'],
        'H0':           cfg.W0WA['H0'],
        'sigma8':       cfg.W0WA['sigma8'],
        'w0':           cfg.W0WA['w0'],
        'wa':           cfg.W0WA['wa'],
        'ns':           cfg.W0WA['ns'],
        'ombh2':        cfg.W0WA['ombh2'],
        'ln10As':       cfg.W0WA['ln10As'],
        'tau':          cfg.W0WA['tau'],
    },
}

out_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'report', 'chains')
os.makedirs(out_dir, exist_ok=True)

rng = np.random.default_rng(RNG_SEED)
summary_lines = []
for model_name, params in MODEL_PARAMS.items():
    arr = {}
    for pname, (mean, sigma) in params.items():
        arr[pname] = rng.normal(mean, sigma, N)
    # save .npz
    np.savez(os.path.join(out_dir, f'{model_name}.chains.npz'), **arr)
    # save getdist-compatible text: one header line with parameter names,
    # then N rows of samples.
    names = list(params.keys())
    text_path = os.path.join(out_dir, f'{model_name}.chains.getdist')
    with open(text_path, 'w') as f:
        f.write('# simulated_getdist_chain\n')
        f.write(' '.join(names) + '\n')
        for i in range(N):
            f.write(' '.join(f'{arr[n][i]:.10e}' for n in names) + '\n')
    summary_lines.append((model_name, len(names), N))

print('Wrote simulated chains:')
for name, npar, n in summary_lines:
    print(f"  {name}: {npar} parameters x {n} samples")
print('Location:', out_dir)
