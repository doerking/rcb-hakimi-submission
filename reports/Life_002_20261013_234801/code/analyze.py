"""
Life_002 · Foldseek-Multimer alignment analysis: 7xg4 (query) vs 6n40 (target).

Produces real measurements (chain composition, sequence identity, TM-score,
runtime) and generates the numbers needed for the report.

Runs single-core. Outputs JSON + console summary.
"""
import json
import math
import os
import re
import time
from collections import defaultdict, OrderedDict

import numpy as np

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
QUERY_PDB = "7xg4.pdb"
TARGET_PDB = "6n40.pdb"

THREE_TO_ONE = {
    "ALA": "A", "ARG": "R", "ASN": "N", "ASP": "D", "CYS": "C",
    "GLN": "Q", "GLU": "E", "GLY": "G", "HIS": "H", "ILE": "I",
    "LEU": "L", "LYS": "K", "MET": "M", "PHE": "F", "PRO": "P",
    "SER": "S", "THR": "T", "TRP": "W", "TYR": "Y", "VAL": "V",
    "SEC": "U", "PYL": "O",
}


# --------------------------------------------------------------------------- #
# PDB parsing
# --------------------------------------------------------------------------- #
def parse_pdb(path):
    """Return {chain_id: {'seq': str, 'ca': (N,3) ndarray, 'resnums': list}}."""
    chains = defaultdict(lambda: {"seq": "", "ca": [], "resnums": [], "atomn": 0})
    with open(path) as f:
        for line in f:
            if not line.startswith("ATOM"):
                continue
            try:
                name = line[12:16].strip()
                chain = line[21]
                resnum_str = line[22:26].strip()
                x = float(line[30:38])
                y = float(line[38:46])
                z = float(line[46:54])
            except ValueError:
                continue
            if not chain or not resnum_str:
                continue
            chains[chain]["atomn"] += 1
            if name == "CA":
                # residue name at cols 17-20; standard 3-letter -> 1-letter
                res_name = line[17:20].strip()
                chains[chain]["seq"] += THREE_TO_ONE.get(res_name, "X")
                chains[chain]["ca"].append((x, y, z))
                try:
                    chains[chain]["resnums"].append(int(resnum_str))
                except ValueError:
                    pass
    for c in chains:
        chains[c]["ca"] = np.asarray(chains[c]["ca"], dtype=float)
    return chains


def parse_chain_order(path):
    """Return (HEADER title, list of chain letters mentioned in COMPND in order)."""
    title_parts, chain_order = [], []
    with open(path) as f:
        for line in f:
            if line.startswith("TITLE"):
                title_parts.append(line[10:].strip())
            elif line.startswith("COMPND") and "CHAIN" in line:
                # extract chain letters
                m = re.search(r"CHAIN:\s*([^;]+)", line)
                if m:
                    for c in m.group(1).replace(",", " ").split():
                        if c.strip() and c.strip() not in chain_order:
                            chain_order.append(c.strip())
    return " ".join(title_parts), chain_order


# --------------------------------------------------------------------------- #
# Sequence identity
# --------------------------------------------------------------------------- #
def seq_identity(a_seq, b_seq):
    """Fraction identity between two strings, using optimal offset window.

    Uses a cheap global-length comparison: normalize to same-length window
    of the shorter sequence, aligned at start. In absence of an actual
    alignment (Foldseek would supply it), we use best-overlap identity
    across a range of shifts.
    """
    if not a_seq or not b_seq:
        return 0.0, 0
    short, long_ = (a_seq, b_seq) if len(a_seq) <= len(b_seq) else (b_seq, a_seq)
    L = len(short)
    if L == 0:
        return 0.0, 0
    best = 0
    best_shift = 0
    for shift in range(0, len(long_) - L + 1):
        matches = sum(1 for i in range(L) if short[i] == long_[shift + i])
        ident = matches / L
        if ident > best:
            best = ident
            best_shift = shift
    return best, best_shift


# --------------------------------------------------------------------------- #
# TM-score (single-chain pairwise, TM-align paper equation)
# --------------------------------------------------------------------------- #
def tm_score(q_ca, t_ca, L_ref=None):
    """Compute TM-score between two CA trajectories (rigid RMSD minimization).

    L_ref defaults to len(q_ca). Uses Zhang & Skolnick TM-score equation:
      d0 = 0.5 * (1.24 * (L_ref - 15)**(1/3) + 8)**2
      TM = 1 / N * sum_i 1 / (1 + d_i^2 / d0^2)
    """
    N = min(len(q_ca), len(t_ca))
    if N < 3:
        return 0.0, 0.0, None, None
    if L_ref is None:
        L_ref = len(q_ca)
    d0 = 0.5 * (1.24 * (L_ref - 15) ** (1.0 / 3.0) + 8) ** 2
    # Superposition via Kabsch (SVD)
    q = q_ca[:N] - q_ca[:N].mean(axis=0)
    t = t_ca[:N] - t_ca[:N].mean(axis=0)
    H = q.T @ t
    U, S, Vt = np.linalg.svd(H)
    d = np.linalg.det(Vt.T @ U.T)
    sign = np.diag([1, 1, np.sign(d)])
    R = Vt.T @ sign @ U.T
    t_aligned = t @ R
    distances = np.linalg.norm(q - t_aligned, axis=1)
    d2 = distances ** 2
    terms = 1.0 / (1.0 + d2 / d0)
    tm = terms.mean()
    rmsd = float(np.sqrt(d2.mean()))
    return float(tm), rmsd, R, (q_ca[:N].mean(axis=0) - t.mean(axis=0))


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def main():
    t0 = time.perf_counter()
    query = parse_pdb(os.path.join(DATA_DIR, QUERY_PDB))
    target = parse_pdb(os.path.join(DATA_DIR, TARGET_PDB))
    parse_time = time.perf_counter() - t0

    # Identify protein chains (those with meaningful CA count)
    def protein_chains(chains):
        return {c: v for c, v in chains.items() if len(v["ca"]) >= 20}

    q_prot = protein_chains(query)
    t_prot = protein_chains(target)

    print(f"\n=== Chain composition ===")
    print(f"Query  ({QUERY_PDB}): {len(query)} total chains, "
          f"{len(q_prot)} protein chains with >=20 CA")
    for c in sorted(q_prot):
        print(f"    chain {c}: {len(q_prot[c]['ca'])} CA residues")
    print(f"Target ({TARGET_PDB}): {len(target)} total chains, "
          f"{len(t_prot)} protein chains with >=20 CA")
    for c in sorted(t_prot):
        print(f"    chain {c}: {len(t_prot[c]['ca'])} CA residues")

    # Sequence identity between query protein chains and the single target chain
    t_chain = sorted(t_prot.keys())[0]
    t_seq = t_prot[t_chain]["seq"]

    seq_results = OrderedDict()
    t1 = time.perf_counter()
    for qc in sorted(q_prot):
        q_seq = q_prot[qc]["seq"]
        ident, shift = seq_identity(q_seq, t_seq)
        seq_results[qc] = {
            "ident": round(ident, 4),
            "shift": shift,
            "len_q": len(q_seq),
            "len_t": len(t_seq),
        }
    seq_time = time.perf_counter() - t1

    print(f"\n=== Sequence identity (query protein chain vs target chain {t_chain}) ===")
    for qc, r in seq_results.items():
        print(f"    {qc}: {r['ident']*100:.2f}%  (len {r['len_q']} vs {r['len_t']})")

    # TM-score per chain pair
    tm_results = OrderedDict()
    t2 = time.perf_counter()
    for qc in sorted(q_prot):
        tm, rmsd, R, trans = tm_score(q_prot[qc]["ca"], t_prot[t_chain]["ca"])
        tm_results[qc] = {
            "tm": round(tm, 4),
            "rmsd": round(rmsd, 2),
            "translation_angstrom": round(float(np.linalg.norm(trans)), 2),
            "rotation_matrix": [[round(float(v), 3) for v in row] for row in R],
        }
    tm_time = time.perf_counter() - t2

    print(f"\n=== TM-score (query chain vs target chain {t_chain}) ===")
    for qc, r in tm_results.items():
        print(f"    {qc}: TM={r['tm']:.4f}  RMSD={r['rmsd']:.2f} A  "
              f"translation={r['translation_angstrom']:.2f} A")

    # Complex-level TM: concatenate all query CA to one structure, compare to target
    q_all = np.vstack([q_prot[c]["ca"] for c in sorted(q_prot)])
    t_all = t_prot[t_chain]["ca"]
    complex_tm, complex_rmsd, _, _ = tm_score(q_all, t_all, L_ref=len(q_all))
    total_time = time.perf_counter() - t0

    print(f"\n=== Complex-level (all query chains vs target chain {t_chain}) ===")
    print(f"    Total query CA: {len(q_all)}   target CA: {len(t_all)}")
    print(f"    Complex TM (query-length normalized): {complex_tm:.4f}")
    print(f"    Complex RMSD: {complex_rmsd:.2f} A")

    print(f"\n=== Timing (single core, this script) ===")
    print(f"    Parse time:         {parse_time:.3f} s")
    print(f"    Seq identity time:  {seq_time:.3f} s")
    print(f"    TM-score time:      {tm_time:.3f} s")
    print(f"    Total wall:         {total_time:.3f} s")

    # Save results
    out = {
        "query_file": QUERY_PDB,
        "target_file": TARGET_PDB,
        "query_protein_chains": sorted(q_prot.keys()),
        "target_protein_chains": sorted(t_prot.keys()),
        "n_query_protein_chains": len(q_prot),
        "n_target_protein_chains": len(t_prot),
        "query_chain_lengths": {c: len(q_prot[c]["ca"]) for c in sorted(q_prot)},
        "target_chain_lengths": {c: len(t_prot[c]["ca"]) for c in sorted(t_prot)},
        "sequence_identity": seq_results,
        "tm_score_per_chain": tm_results,
        "complex_tm_score": round(complex_tm, 4),
        "complex_rmsd": round(complex_rmsd, 2),
        "timing": {
            "parse_s": round(parse_time, 3),
            "seq_id_s": round(seq_time, 3),
            "tm_s": round(tm_time, 3),
            "total_s": round(total_time, 3),
        },
    }
    with open(os.path.join(os.path.dirname(__file__), "analysis_results.json"), "w") as f:
        json.dump(out, f, indent=2)
    print("\nSaved: analysis_results.json")
    return out


if __name__ == "__main__":
    main()
