"""Parse XYZ files (no blank-line separator). Each frame:
   n_atoms
   Properties=... [energy=..] [charge_state=..] [true_charges=".."] pbc="F F F"
   atom_line * n_atoms  (species, x,y,z, fx,fy,fz)
"""
import re, json, sys
from pathlib import Path

def parse_xyz(path):
    with open(path) as f:
        txt = f.read()
    lines = [l.rstrip() for l in txt.split('\n') if l.strip()]
    frames = []
    i = 0
    while i < len(lines):
        try:
            n = int(lines[i])
        except ValueError:
            i += 1; continue
        header = lines[i+1]
        atoms = []
        for k in range(n):
            parts = lines[i+2+k].split()
            atoms.append({
                'species': parts[0],
                'pos': [float(parts[1]), float(parts[2]), float(parts[3])],
                'force': [float(parts[4]), float(parts[5]), float(parts[6])] if len(parts) >= 7 else [0.0,0.0,0.0]
            })
        frames.append({
            'n': n, 'header': header, 'atoms': atoms,
            'energy': float(re.search(r'energy=([-\d.]+)', header).group(1)) if 'energy=' in header else None,
            'charge_state': int(re.search(r'charge_state=(-?\d+)', header).group(1)) if 'charge_state=' in header else None,
            'total_charge': float(re.search(r'total_charge=([-\d.]+)', header).group(1)) if 'total_charge=' in header else None,
            'true_charges': [float(x) for x in re.search(r'true_charges="([^"]+)"', header).group(1).split()] if 'true_charges=' in header else None,
        })
        i += 2 + n
    return frames

def summarize(path):
    frames = parse_xyz(path)
    print(f'=== {path} === {len(frames)} frames')
    energies = [f['energy'] for f in frames if f['energy'] is not None]
    if energies:
        print(f'  energy: min={min(energies):.4f} max={max(energies):.4f} mean={sum(energies)/len(energies):.4f}')
    if any(f['charge_state'] is not None for f in frames):
        from collections import Counter
        c = Counter(f['charge_state'] for f in frames)
        print(f'  charge_state distribution: {dict(c)}')
    if frames[0]['true_charges'] is not None:
        tc = frames[0]['true_charges']
        pos = sum(1 for x in tc if x > 0); neg = sum(1 for x in tc if x < 0)
        print(f'  frame0 true_charges: n+={pos} n-={neg} n0={len(tc)-pos-neg}')
    # Print first frame details
    f0 = frames[0]
    print(f'  frame0 atoms:')
    for a in f0['atoms'][:5]:
        print(f'    {a}')
    return frames

if __name__ == '__main__':
    for p in ['data/random_charges.xyz', 'data/charged_dimer.xyz', 'data/ag3_chargestates.xyz']:
        summarize(p)
        print()
