import sys; sys.path.insert(0,'code')
from parse_data import parse_xyz
import numpy as np

frames = parse_xyz('data/ag3_chargestates.xyz')
cs1 = [f for f in frames if f['charge_state']==1]
cs2 = [f for f in frames if f['charge_state']==-1]

def sig(f):
    return tuple(tuple(round(x,6) for x in p) for p in [a['pos'] for a in f['atoms']])

print('charge_state=+1 (first 5):')
for f in cs1[:5]:
    pos = [[round(x,3) for x in p] for p in [a['pos'] for a in f['atoms']]]
    print(f'  E={f["energy"]:.4f}  pos={pos}')
print('charge_state=-1 (first 5):')
for f in cs2[:5]:
    pos = [[round(x,3) for x in p] for p in [a['pos'] for a in f['atoms']]]
    print(f'  E={f["energy"]:.4f}  pos={pos}')

# Are the positions shared?
cs1_sigs = [sig(f) for f in cs1]
cs2_sigs = [sig(f) for f in cs2]
overlap = set(cs1_sigs).intersection(set(cs2_sigs))
print(f'\n+1 unique positions: {len(set(cs1_sigs))}')
print(f'-1 unique positions: {len(set(cs2_sigs))}')
print(f'shared positions: {len(overlap)}')

# Energy difference at same geometry
print('\nEnergy differences at shared geometries:')
for sig_p in list(overlap)[:5]:
    e1 = [f['energy'] for f in cs1 if sig(f) == sig_p][0]
    e2 = [f['energy'] for f in cs2 if sig(f) == sig_p][0]
    print(f'  E(+1)={e1:.4f}  E(-1)={e2:.4f}  diff={e1-e2:.4f}')

# Average energy difference
diffs = []
for sig_p in overlap:
    e1 = [f['energy'] for f in cs1 if sig(f) == sig_p][0]
    e2 = [f['energy'] for f in cs2 if sig(f) == sig_p][0]
    diffs.append(e1 - e2)
print(f'\nEnergy diff (+1 minus -1): mean={np.mean(diffs):.4f} eV, std={np.std(diffs):.4f}')
