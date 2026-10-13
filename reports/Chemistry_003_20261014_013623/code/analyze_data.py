"""Analyze the three datasets to extract the underlying physics.
Outputs raw quantities needed for the figures.
"""
import numpy as np, json
from pathlib import Path
import sys
sys.path.insert(0, Path(__file__).parent)
from parse_data import parse_xyz

# --------- Charged dimer ---------
frames = parse_xyz('data/charged_dimer.xyz')
print(f'=== charged_dimer: {len(frames)} frames ===')
seps = []
energies = []
dipoles = []
for f in frames:
    pos = np.array([a['pos'] for a in f['atoms']])
    species = [a['species'] for a in f['atoms']]
    # find the two C atoms
    ci = [i for i,s in enumerate(species) if s=='C']
    if len(ci) == 2:
        d = np.linalg.norm(pos[ci[0]] - pos[ci[1]])
    else:
        d = np.linalg.norm(pos[0] - pos[-1])
    seps.append(d)
    energies.append(f['energy'])
    # charge-weighted dipole: first half atoms carry +1/total, second half -1/total
    half = len(species)//2
    qvec = np.zeros(len(species))
    qvec[:half] = 1.0 / half
    qvec[half:] = -1.0 / (len(species)-half)
    dip = np.sum(qvec[:,None] * pos, axis=0)
    dipoles.append(np.linalg.norm(dip))
seps = np.array(seps); energies = np.array(energies); dipoles = np.array(dipoles)
print(f'separation: {seps.min():.3f} - {seps.max():.3f}')
print(f'energy: {energies.min():.3f} - {energies.max():.3f}')
print(f'dipole: {dipoles.min():.3f} - {dipoles.max():.3f}')
# bin by 0.5 Angstrom
bins = np.arange(3, 13, 0.5)
idx = np.digitize(seps, bins)
print('binned (sep, E, N):')
for i, b in enumerate(bins[:-1]):
    m = idx == i
    if m.any():
        print(f'  sep=[{b:.1f},{b+0.5:.1f}) N={m.sum()}  <E>={energies[m].mean():.3f}  E_min={energies[m].min():.3f}  E_max={energies[m].max():.3f}')

# --------- Ag3 ---------
print('\n=== ag3: ===')
frames = parse_xyz('data/ag3_chargestates.xyz')
data_by_cs = {1: [], -1: []}
for f in frames:
    pos = np.array([a['pos'] for a in f['atoms']])
    # pairwise distances
    d01 = np.linalg.norm(pos[0]-pos[1])
    d12 = np.linalg.norm(pos[1]-pos[2])
    d02 = np.linalg.norm(pos[0]-pos[2])
    avg_d = (d01 + d12 + d02) / 3.0
    data_by_cs[f['charge_state']].append((avg_d, f['energy']))
for cs, arr in data_by_cs.items():
    arr = np.array(arr)
    print(f'  charge_state={cs}: N={len(arr)}, r_avg=[{arr[:,0].min():.3f},{arr[:,0].max():.3f}], E=[{arr[:,1].min():.3f},{arr[:,1].max():.3f}]')
    # E vs r
    arr_sorted = arr[np.argsort(arr[:,0])]
    print(f'    first 3 sorted: {arr_sorted[:3]}')
    print(f'    last  3 sorted: {arr_sorted[-3:]}')
    # find minimum
    imin = np.argmin(arr[:,1])
    print(f'    min E={arr[imin,1]:.3f} at r={arr[imin,0]:.3f}')

# --------- Random charges ---------
print('\n=== random_charges: ===')
frames = parse_xyz('data/random_charges.xyz')
print(f'frames={len(frames)}')
# check charge balance
for i, f in enumerate(frames[:3]):
    tc = f['true_charges']
    s = sum(tc)
    print(f'  frame[{i}] sum={s:.3f}, first10={tc[:10]}, last10={tc[-10:]}')
