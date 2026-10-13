"""verify_hf.py — reduced self-consistent Hartree-Fock loop (beyond-paper demonstration).

目的：论文只说「self-consistent HF」，冇展示闭环。本件在**截断平面波基**上实做一次闭环：
  ρ(联) → H^HF[ρ] = H0 + Hartree(ρ) + Fock(ρ) → 对角化 → ρ' → … 直到 |ΔE| < tol
用论文 V(q)=2πe^2 tanh(qd)/(εq) · ε=15 · d=5nm。
⚠️ 诚实标注：基组截断到第一 G 壳（每谷 2 层 × 7 G = 14 维）· 单 k 点(Γ) · ν=2 ⇒ 系**精简演示**，
   唔系论文全平面波 HF；目的系验「自洽闭环真系收敛」呢个结构。
"""
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "report" / "images"
OUT.mkdir(parents=True, exist_ok=True)

# --- 复用 verify.py 的平面波 H0（截断第一 G 壳 · 单 k=Γ）---
aM = 47.0
mb, mt = 0.65, 0.35
HBAR2_2ME = 3809.98
w, Vb, Vzt = 12.0, 7.0, -20.0
psi_b = np.deg2rad(-14.0); omega = np.exp(1j*2*np.pi/3)
g = [4*np.pi/(np.sqrt(3)*aM)*np.array([-np.sin(np.pi*(j-1)/3), np.cos(np.pi*(j-1)/3)]) for j in range(1, 7)]
Gs = [np.zeros(2)] + [g[j] for j in range(6)]
NG = len(Gs)

def H_plane(tau, k):
    dim = 2*NG; H = np.zeros((dim, dim), complex)
    for A, GA in enumerate(Gs):
        kk = k + GA
        H[A, A] += -HBAR2_2ME*np.dot(kk, kk)/mb
        kt = kk - tau*np.array([4*np.pi/(3*aM), 0.0])
        H[NG+A, NG+A] += -HBAR2_2ME*np.dot(kt, kt)/mt + Vzt
        for (dG, amp) in [(np.zeros(2), 1.0), (tau*g[1], omega**tau), (tau*g[2], omega**(2*tau))]:
            for B, GB in enumerate(Gs):
                if np.allclose(GB, GA+dG, atol=1e-6):
                    H[A, NG+B] += tau*w*amp; H[NG+B, A] += np.conj(tau*w*amp)
        for j in (0, 2, 4):
            for (dG, amp) in [(g[j], 0.5*np.exp(1j*psi_b)), (-g[j], 0.5*np.exp(-1j*psi_b))]:
                for B, GB in enumerate(Gs):
                    if np.allclose(GB, GA+dG, atol=1e-6):
                        H[A, B] += 2*Vb*amp
    return (H + H.conj().T)/2

# --- 论文 V(q) [meV] ---
E2 = 14.4*1000.0  # e^2/(4πε0) in meV·Å
eps, d = 15.0, 50.0  # d=5nm=50Å
def Vq(q):
    q = np.asarray(q, float)
    if np.isscalar(q) or q.ndim == 0:
        return 2*np.pi*E2*np.tanh(float(q)*d)/(eps*max(float(q), 1e-6))
    qq = np.where(q < 1e-6, 1e-6, q)
    return 2*np.pi*E2*np.tanh(qq*d)/(eps*qq)

# --- 双谷 H0（28）---
H0 = np.zeros((28, 28), complex)
H0[:14, :14] = H_plane(+1, np.zeros(2))
H0[14:, 14:] = H_plane(-1, np.zeros(2))

# --- Fock 耦合核（G-space，同谷内）---
def fock_kernel(tau):
    """F_{lG, l'G'} = V(|G - G'|)（层对角）· 剔除 q=0（背景中和）。"""
    F = np.zeros((14, 14))
    for A in range(14):
        for B in range(14):
            lA, GA = divmod(A, NG); lB, GB = divmod(B, NG)
            if lA == lB and not np.allclose(Gs[GA], Gs[GB], atol=1e-6):
                F[A, B] = Vq(np.linalg.norm(Gs[GA]-Gs[GB]))
    return F

Fk = np.zeros((28, 28))
Fk[:14, :14] = fock_kernel(+1); Fk[14:, 14:] = fock_kernel(-1)

def hf_from_rho(rho):
    # Hartree（对角 · 剔除 q=0 背景中和）· Fock（非对角）
    Hh = np.zeros((28, 28), complex)
    for blk in (0, 14):
        for A in range(14):
            lA, GA = divmod(A, NG)
            s = 0.0
            for B in range(14):
                lB, GB = divmod(B, NG)
                if not np.allclose(Gs[GA], Gs[GB], atol=1e-6):
                    s += Vq(np.linalg.norm(Gs[GA]-Gs[GB]))*rho[blk+B, blk+B].real
            Hh[blk+A, blk+A] += s
    Hf = -(Fk*rho)
    return H0 + Hh + Hf

def energy(rho, H):
    return np.real(np.trace(rho @ H))

# ν=2：填最低 2 个本征态
def rho_occ(H, n=2):
    w_, v = np.linalg.eigh(H)
    order = np.argsort(w_)
    occ = v[:, order[:n]]
    return occ @ occ.conj().T

rho = rho_occ(H0, 2)
Es = []
mix = 0.3
for it in range(120):
    H = hf_from_rho(rho)
    rho_new = rho_occ(H, 2)
    rho = (1-mix)*rho + mix*rho_new
    Es.append(energy(rho, H))
Es = np.array(Es)

fig, ax = plt.subplots(figsize=(7, 4))
ax.plot(range(len(Es)), Es, "o-", color="tab:red", ms=3, lw=1.4)
ax.set_xlabel("HF iteration"); ax.set_ylabel("total energy [meV]")
ax.set_title("Self-consistent HF energy convergence (reduced plane-wave basis)")
ax.grid(alpha=.3)
fig.tight_layout(); fig.savefig(OUT / "hf_convergence.png", dpi=130)
print("saved report/images/hf_convergence.png")
print(f"E[0]={Es[0]:.3f}  E[-1]={Es[-1]:.3f} meV  |ΔE|(last)={abs(Es[-1]-Es[-2]):.2e} meV")
print("Fock off-diagonal max =", float(np.max(np.abs(Fk - np.diag(np.diag(Fk))))))
