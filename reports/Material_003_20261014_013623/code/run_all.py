"""Master orchestrator for Material_003 figure reproduction.

Run this to regenerate all figures:
    py -3.11 code/run_all.py
"""
import subprocess
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

scripts = [
    'run_gp.py',            # GP LOOCV cache (only if missing)
    'figure_1_framework.py',
    'figure_2_vae_bo.py',
    'figure_3_experiment.py',
    'figure_tanimoto_gp.py',
]

for s in scripts:
    path = os.path.join(SCRIPT_DIR, s)
    print(f'\n>>> Running {s}...')
    r = subprocess.run([sys.executable, path], cwd=SCRIPT_DIR)
    if r.returncode != 0:
        print(f'FAILED: {s}')
        sys.exit(r.returncode)
    print(f'OK: {s}')

print('\nAll figures generated successfully.')
print('Output directory:', os.path.join(
    os.path.dirname(SCRIPT_DIR), 'report', 'images'))
