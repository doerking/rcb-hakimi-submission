"""
make_figures.py
================
Generates two illustrations for `report/images/`:

  1. imo2004p1_baseline.png    — the classical IMO 2004 P1 configuration
                                 with O = midpoint(BC).
  2. imo2004p1_invariance.png  — the "more general theorem": O varies along
                                 the perpendicular bisector of BC, yet P
                                 stays at the *same* point.
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from trace_back import Pt, solve_imo04p1, smul, dist, unit, \
    second_circle_line, circumcenter, intersect_circles  # noqa: F401


def midpoint(A: Pt, B: Pt) -> Pt:
    return Pt((A.x + B.x) / 2, (A.y + B.y) / 2)


def draw_configuration(ax, A, B, C, O, M, N, R, c1, r1, c2, r2, P,
                       show_labels=True):
    """Draw a full IMO 2004 P1 construction into `ax`."""
    # base triangle
    tri_x = [A.x, B.x, C.x, A.x]
    tri_y = [A.y, B.y, C.y, A.y]
    ax.plot(tri_x, tri_y, color="#1f3b73", lw=1.6, zorder=2, label="triangle ABC")
    # circle(O, OB)
    OB = dist(O, B)
    theta = np.linspace(0, 2 * np.pi, 400)
    ax.plot(O.x + OB * np.cos(theta), O.y + OB * np.sin(theta),
            color="#888", lw=1.0, ls="--", alpha=0.8, zorder=1,
            label="circle(O, OB)")
    # circumcircles O1 (B,M,R), O2 (C,N,R)
    for cc, rr, lbl, col in [(c1, r1, "O₁ (BMR)", "#e07b39"),
                              (c2, r2, "O₂ (CNR)", "#4d8f3a")]:
        ax.plot(cc.x + rr * np.cos(theta), cc.y + rr * np.sin(theta),
                color=col, lw=1.1, alpha=0.8, zorder=1, label=lbl)
    # auxiliary lines
    for P1, P2, col, ls in [(M, R, "#777", ":"), (N, R, "#777", ":")]:
        ax.plot([P1.x, P2.x], [P1.y, P2.y], color=col, lw=0.8, ls=ls)
    # angle bisector from A (through R)
    if R is not None:
        dirA = unit(R - A)
        ax.plot([A.x - 3 * dirA.x, A.x + 3 * dirA.x],
                [A.y - 3 * dirA.y, A.y + 3 * dirA.y],
                color="#c14", lw=0.8, ls="--", alpha=0.6,
                label="bisector of ∠BAC")
    # points
    pts = {"A": A, "B": B, "C": C, "O": O, "M": M, "N": N, "R": R,
           "P": P}
    for lbl, pt in pts.items():
        if pt is None:
            continue
        if lbl in ("A", "B", "C"):
            ax.plot([pt.x], [pt.y], "o", ms=8, color="#1f3b73", zorder=4)
        elif lbl == "P":
            ax.plot([pt.x], [pt.y], "s", ms=9, color="#d11", zorder=5,
                    label="P (conclusion point)")
        else:
            ax.plot([pt.x], [pt.y], "o", ms=6, color="#c14", zorder=4)
        if show_labels:
            ax.annotate(lbl, (pt.x, pt.y),
                        xytext=(6, 4), textcoords="offset points",
                        fontsize=10, zorder=6)


def make_baseline():
    """IMO 2004 P1 with O = midpoint(BC)."""
    A, B, C = Pt(2.0, 10.0), Pt(-5.0, 0.0), Pt(5.0, 0.0)
    O = midpoint(B, C)
    OB = dist(O, B)
    rM = second_circle_line(A, B, O, OB)
    M = next(p for p in rM if dist(p, B) > 1e-6)
    rN = second_circle_line(A, C, O, OB)
    N = next(p for p in rN if dist(p, C) > 1e-6)
    uB = unit(B - A); uC = unit(C - A); bdir = uB + uC
    uM = unit(M - O); uN = unit(N - O); mdir = uM + uN
    Amat = np.array([[bdir.x, -mdir.x], [bdir.y, -mdir.y]])
    s = np.linalg.solve(Amat, np.array([O.x - A.x, O.y - A.y]))
    R = A + smul(float(s[0]), bdir)
    c1 = circumcenter(B, M, R); r1 = dist(B, c1)
    c2 = circumcenter(C, N, R); r2 = dist(C, c2)
    Ppts = intersect_circles(c1, r1, c2, r2)
    P = next(p for p in Ppts if abs((p.x - B.x) * (C.y - B.y)
                                    - (p.y - B.y) * (C.x - B.x)) < 1e-4)

    fig, ax = plt.subplots(figsize=(8, 6.4), dpi=140)
    draw_configuration(ax, A, B, C, O, M, N, R,
                       c1, r1, c2, r2, P)
    ax.set_title("IMO 2004 P1 — baseline  (O = midpoint of BC)\n"
                 "P lies on line BC, as required.",
                 fontsize=11)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.legend(loc="upper left", fontsize=9, framealpha=0.9)
    fig.tight_layout()
    out = HERE.parent / "report" / "images" / "imo2004p1_baseline.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out)
    plt.close(fig)
    print(f"wrote {out}")


def make_invariance():
    """Show P is invariant under O along the perpendicular bisector of BC."""
    A, B, C = Pt(2.0, 10.0), Pt(-5.0, 0.0), Pt(5.0, 0.0)
    Bc = Pt((B.x + C.x) / 2, (B.y + C.y) / 2)
    dir_bc = unit(C - B)
    perp = Pt(-dir_bc.y, dir_bc.x)

    fig, axes = plt.subplots(1, 3, figsize=(15, 5.4), dpi=140)
    for ax, t in zip(axes, [-4.0, 0.0, 5.0]):
        O = Bc + smul(t, perp)
        P, msg, info = solve_imo04p1(A, B, C, O)
        if msg != "OK":
            ax.set_title(f"O = {O}  ({msg})", fontsize=10)
            continue
        ax.plot([A.x, B.x, C.x, A.x], [A.y, B.y, C.y, A.y],
                color="#1f3b73", lw=1.4, zorder=2)
        # circle(O, OB)
        OB = dist(O, B)
        theta = np.linspace(0, 2 * np.pi, 400)
        ax.plot(O.x + OB * np.cos(theta), O.y + OB * np.sin(theta),
                color="#888", lw=0.9, ls="--", alpha=0.7, zorder=1)
        # circles O1 and O2 (thin, to keep plot readable)
        c1 = info["O1"][0]; r1 = info["O1"][1]
        c2 = info["O2"][0]; r2 = info["O2"][1]
        for cc, rr, col in [(c1, r1, "#e07b39"), (c2, r2, "#4d8f3a")]:
            ax.plot(cc.x + rr * np.cos(theta), cc.y + rr * np.sin(theta),
                    color=col, lw=0.9, alpha=0.6, zorder=1)
        M, N, R = info["M"], info["N"], info["R"]
        # lines to R
        ax.plot([M.x, R.x], [M.y, R.y], color="#777", lw=0.7, ls=":")
        ax.plot([N.x, R.x], [N.y, R.y], color="#777", lw=0.7, ls=":")
        # points
        for lbl, pt in [("A", A), ("B", B), ("C", C), ("O", O),
                        ("M", M), ("N", N), ("R", R)]:
            ax.plot([pt.x], [pt.y], "o", ms=5, color="#c14"
                    if lbl not in "ABC" else "#1f3b73", zorder=4)
            ax.annotate(lbl, (pt.x, pt.y),
                        xytext=(5, 3), textcoords="offset points",
                        fontsize=9, zorder=6)
        # P emphasized
        ax.plot([P.x], [P.y], "s", ms=11, color="#d11", zorder=6,
                label="P")
        ax.annotate(f"P = ({P.x:.3f}, {P.y:.3f})", (P.x, P.y),
                    xytext=(6, 5), textcoords="offset points",
                    fontsize=9, color="#d11", zorder=7)
        # perpendicular bisector hint
        ax.plot([Bc.x - 8 * perp.x, Bc.x + 8 * perp.x],
                [Bc.y - 8 * perp.y, Bc.y + 8 * perp.y],
                color="#080", lw=0.5, ls=":", alpha=0.5,
                label="⊥ bisector of BC")
        ax.set_title(f"O = {O}   (t = {t:+.1f})\n"
                     f"P = ({P.x:.4f}, {P.y:.4f})", fontsize=10)
        ax.set_aspect("equal"); ax.axis("off")
        ax.legend(loc="upper right", fontsize=8)

    fig.suptitle("IMO 2004 P1 generalisation: P is INVARIANT under O "
                 "along the perpendicular bisector of BC",
                 fontsize=12, y=1.02)
    fig.tight_layout()
    out = HERE.parent / "report" / "images" / "imo2004p1_invariance.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {out}")


if __name__ == "__main__":
    make_baseline()
    make_invariance()
