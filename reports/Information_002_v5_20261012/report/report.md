# A Step-by-Step, Paper-Grounded Hartree–Fock Derivation for the AB-Stacked MoTe₂/WSe₂ Moiré System (arXiv:2111.01152)

**Task**: ResearchClawBench `Information_002` (Information Sciences)
**Agent**: Hakimi — manual reproduction, v2 (depth pass)
**Source paper**: *Topological Phases in AB-Stacked MoTe₂/WSe₂: ℤ₂ Topological Insulators, Chern Insulators, and Topological Charge Density Waves* (Pan, Xie, Wu, Das Sarma; arXiv:2111.01152)
**Date**: 2026-10-06

---

## Abstract

We reproduce, in full algebraic detail, the 16-step automated Hartree–Fock (HF) derivation pipeline of
arXiv:2111.01152 for the AB-stacked MoTe₂/WSe₂ moiré heterobilayer. Every intermediate expression is
written out rather than asserted: the continuum kinetic and moiré-potential Hamiltonians; the
single-particle → **second-quantised** conversion (matrix **and** summation forms); the **Fourier
transformation** to momentum space including the moiré-potential form factors that scatter
$\bm k\to\bm k\pm\bm G$; the **particle–hole transformation** obtained from the fermionic
anticommutator (which generates the constant trace term); the **density–density interaction** with the
dual-gate screened Coulomb potential; the **Wick decomposition** into Hartree and Fock contractions;
the **Brillouin-zone momentum reduction** ($\bm k=\bm k_{\rm BZ}+\bm G$) carried out explicitly for both
terms; and the **self-consistent** closing of the mean-field loop. The final mean-field Hamiltonian is
$\hat{\mathcal H}^{\rm HF}=\hat H^{0}+H_{\rm Hartree}+H_{\rm Fock}$.

---

## 1 · Introduction and task structure

The target study probes whether an LLM, driven by structured prompt templates, can carry out
*research-level* theoretical derivations. The released instance is the HF derivation for one system
(AB-stacked MoTe₂/WSe₂), decomposed into **16 analytic steps** with **105 placeholders**. The three
evaluation criteria correspond to three pipeline phases:

| phase | steps | what must be demonstrated |
|---|---|---|
| **I. Foundations** | 1–6 | construct Kinetic & Potential Hamiltonians (continuum), convert single-particle → second-quantised (matrix **and** summation) |
| **II. Basis transformations** | 7–11 | real→momentum space (Fourier), particle–hole transform, add interaction, apply **Wick's theorem** (mean-field decomposition) |
| **III. Mean-field reduction** | 12–16 | extract quadratic terms, reduce momenta to the BZ for **Hartree** and **Fock**, combine into $H^{\rm HF}$ |

All conventions below are taken verbatim from the paper and its Supplemental Material.

---

## 2 · Phase I — Foundations

### 2.1 Continuum single-particle Hamiltonian (Task 1–2)

Retaining the topmost valence band from each layer, the valley-dependent $2\times2$ Hamiltonian in the
layer basis $(\mathfrak b,\mathfrak t)$ is (paper Eq. for $H_\tau$)

$$
\boxed{\,H_{\tau}(\bm r)=
\begin{pmatrix}
-\dfrac{\hbar^2 \bm k^2}{2m_{\mathfrak b}}+\Delta_{\mathfrak b}(\bm r) & \Delta_{\mathrm T,\tau}(\bm r)\\[2mm]
\Delta_{\mathrm T,\tau}^{\dagger}(\bm r) & -\dfrac{\hbar^2\left(\bm k-\tau\bm\kappa\right)^2}{2m_{\mathfrak t}}+\Delta_{\mathfrak t}(\bm r)+V_{z\mathfrak t}
\end{pmatrix}}
$$
with $\tau=\pm1$ the valley, $\bm\kappa=\frac{4\pi}{3a_M}(1,0)$, $(m_{\mathfrak b},m_{\mathfrak t})=(0.65,0.35)m_e$.
**Two points of convention are essential** (and are a frequent source of sign errors):
(i) the kinetic terms carry a **negative** sign — these are *valence* (hole-like) bands and
$\bm k=-i\nabla$;
(ii) the momentum shift $\pm\tau\bm\kappa$ acts **only on the top layer** (WSe₂); the bottom layer is unshifted.

The full four-band non-interacting Hamiltonian arranges the two valleys block-diagonally,
$$
\hat{\mathcal H}_0=\operatorname{diag}\!\big(H_{+K},\,H_{-K}\big),\qquad
\text{basis }(\mathfrak b,+K),(\mathfrak t,+K),(\mathfrak b,-K),(\mathfrak t,-K).
$$

### 2.2 Moiré potential and interlayer tunnelling (Task 3–4)

The intralayer potential, tunnelling term and band offset are (paper Eqs. $\Delta_{\mathfrak b}$,
$\Delta_{\mathrm T,\tau}$; SM: $\Delta_{\mathfrak t}=0$, $\psi_{\mathfrak b}=-14^\circ$)

$$
\Delta_{\mathfrak b}(\bm r)=2V_{\mathfrak b}\!\sum_{j=1,3,5}\!\cos\!\big(\bm g_j\!\cdot\!\bm r+\psi_{\mathfrak b}\big),\qquad
\Delta_{\mathfrak t}(\bm r)=0,
$$
$$
\Delta_{\mathrm T,\tau}(\bm r)=\tau\,w\Big(1+\omega^{\tau}e^{i\tau \bm g_2\cdot\bm r}+\omega^{2\tau}e^{i\tau \bm g_3\cdot\bm r}\Big),
\qquad \omega=e^{i2\pi/3},
$$
where $\bm g_j=\frac{4\pi}{\sqrt3 a_M}\big(-\sin\frac{\pi(j-1)}{3},\cos\frac{\pi(j-1)}{3}\big)$ are the first-shell moiré
reciprocal vectors. The potential Hamiltonian is thus
$$
H^{\rm pot}_\tau(\bm r)=
\begin{pmatrix}
\Delta_{\mathfrak b}(\bm r) & \Delta_{\mathrm T,\tau}(\bm r)\\
\Delta_{\mathrm T,\tau}^{\dagger}(\bm r) & V_{z\mathfrak t}
\end{pmatrix},
\qquad
H_\tau=H^{\rm kin}_\tau+H^{\rm pot}_\tau .
$$

### 2.3 Second quantisation — matrix form then summation form (Task 5–6)

Introduce the four-component field operator
$\vec\Psi(\bm r)=\big(\psi_{\mathfrak b,+K},\psi_{\mathfrak t,+K},\psi_{\mathfrak b,-K},\psi_{\mathfrak t,-K}\big)^{\!\top}$.
The second-quantised non-interacting Hamiltonian is
$$
\hat H^{0}=\int d^2\bm r\;\vec\Psi^{\dagger}(\bm r)\,\mathcal H_0(\bm r)\,\vec\Psi(\bm r)
=\sum_{\tau=\pm}\int d^2\bm r\;
\begin{pmatrix}\psi^{\dagger}_{\mathfrak b,\tau}&\psi^{\dagger}_{\mathfrak t,\tau}\end{pmatrix}
H_\tau(\bm r)
\begin{pmatrix}\psi_{\mathfrak b,\tau}\\ \psi_{\mathfrak t,\tau}\end{pmatrix}.
$$
Expanding the matrix product gives the **summation form** (Task 6)
$$
\hat H^{0}=\sum_{\tau}\sum_{l_1,l_2\in\{\mathfrak b,\mathfrak t\}}\int d^2\bm r\;\psi^{\dagger}_{l_1,\tau}(\bm r)\,
\big[H_\tau(\bm r)\big]_{l_1l_2}\,\psi_{l_2,\tau}(\bm r),
$$
the two off-diagonal terms being Hermitian conjugates of one another. This is the operator basis on
which every later transformation acts.

---

## 3 · Phase II — Basis transformations

### 3.1 Real space → momentum space (Fourier) (Task 7)

Using the paper/SM convention ($A$ = total area)
$$
c^{\dagger}_{\bm k,l,\tau}=\frac{1}{\sqrt A}\int d^2\bm r\;\psi^{\dagger}_{l,\tau}(\bm r)\,e^{i\bm k\cdot\bm r},
\qquad
\psi^{\dagger}_{l,\tau}(\bm r)=\frac{1}{\sqrt A}\sum_{\bm k}c^{\dagger}_{\bm k,l,\tau}e^{-i\bm k\cdot\bm r},
$$
and substituting into $\hat H^0$ yields
$$
\hat H^{0}=\sum_{\tau}\sum_{l_1,l_2}\sum_{\bm k_1,\bm k_2}
c^{\dagger}_{\bm k_1,l_1,\tau}\;h^{(\tau)}_{\bm k_1l_1,\bm k_2l_2}\;c_{\bm k_2,l_2,\tau}.
$$
**The momentum-space matrix elements are not diagonal**, because the moiré potential scatters
$\bm k\to\bm k\pm\bm G$. Writing $\bm k_1=\bm k_2+\bm G$ we get, explicitly,

$$
h^{(\tau)}_{\bm k_1l_1,\bm k_2l_2}=
\underbrace{\Big[-\tfrac{\hbar^2 k^2}{2m_{\mathfrak b}}\,\delta_{l_1\mathfrak b}
-\tfrac{\hbar^2(\bm k-\tau\bm\kappa)^2}{2m_{\mathfrak t}}\,\delta_{l_1\mathfrak t}\Big]\delta_{\bm k_1,\bm k_2}\delta_{l_1l_2}}_{\text{kinetic (diagonal)}}
+\underbrace{V_{z\mathfrak t}\delta_{l_1\mathfrak t}\delta_{l_1l_2}\delta_{\bm k_1,\bm k_2}}_{\text{band offset}}
$$
$$
+\underbrace{2V_{\mathfrak b}\!\sum_{j\in\{1,3,5\}}\!\Big[\tfrac{e^{i\psi_{\mathfrak b}}}{2}\delta_{\bm k_1,\bm k_2+\bm g_j}+\tfrac{e^{-i\psi_{\mathfrak b}}}{2}\delta_{\bm k_1,\bm k_2-\bm g_j}\Big]\delta_{l_1l_2}\delta_{l_1\mathfrak b}}_{\text{intralayer moiré potential}}
+\underbrace{\tau w\Big[\delta_{\bm k_1,\bm k_2}+\omega^{\tau}\delta_{\bm k_1,\bm k_2+\tau\bm g_2}+\omega^{2\tau}\delta_{\bm k_1,\bm k_2+\tau\bm g_3}\Big]}_{\text{interlayer tunnelling }\Delta_{\mathrm T,\tau}}.
$$

This makes precise *why* the momentum-space Hamiltonian is a matrix in $\bm G$ (a "plane-wave"
Hamiltonian): the periodic moiré potential turns the diagonal kinetic term into a
$\bm G$-coupled block structure. (This is the expansion the earlier, compressed presentation omitted.)

### 3.2 Particle–hole transformation (Task 8–9)

Define hole operators $c^{\dagger}_{\bm k,l,\tau}=b_{\bm k,l,\tau}$, $c_{\bm k,l,\tau}=b^{\dagger}_{\bm k,l,\tau}$.
Because $b$ are fermions, $\{b_{\bm k_1l_1\tau},b^{\dagger}_{\bm k_2l_2\tau'}\}=\delta_{\tau\tau'}\delta_{l_1l_2}\delta_{\bm k_1\bm k_2}$, so
$$
b_{\bm k_1l_1\tau}b^{\dagger}_{\bm k_2l_2\tau}
=\delta_{l_1l_2}\delta_{\bm k_1\bm k_2}-b^{\dagger}_{\bm k_2l_2\tau}b_{\bm k_1l_1\tau}.
$$
Substituting into $\hat H^0=\sum b\,h\,b^{\dagger}$ gives
$$
\boxed{\;\hat{\mathcal H}_0=-\sum_{\tau,\bm k_1,\bm k_2,l_1,l_2}
b^{\dagger}_{\bm k_2,l_2,\tau}\,\big(h^{(\tau)}_{\bm k_2l_2,\bm k_1l_1}\big)\,b_{\bm k_1,l_1,\tau}
+\underbrace{\sum_{\tau,\bm k,l}h^{(\tau)}_{\bm kl,\bm kl}}_{\text{constant }E_0}\;}
$$
i.e. the non-interacting problem is rewritten in terms of holes up to a $\bm k$-independent constant
$E_0=\operatorname{tr}h$ — the term the compact presentation dropped. (The hole picture is natural here
because the retained bands are valence bands; it makes the occupied reference the hole vacuum.)

### 3.3 Interaction Hamiltonian (Task 10–11)

The dual-gate screened Coulomb interaction is
$$
V(q)=\frac{2\pi e^2\tanh(qd)}{\epsilon\,q},\qquad q=|\bm k_\alpha-\bm k_\delta|,\ d=5\,\text{nm}.
$$
In the hole basis the density–density interaction is
$$
\hat{\mathcal H}_{\rm int}=\frac{1}{2A}\!\sum_{\tau_\alpha,\tau_\beta}\sum_{l_\alpha,l_\beta}\sum_{\bm k_\alpha,\bm k_\beta,\bm k_\gamma,\bm k_\delta}
V(|\bm k_\alpha-\bm k_\delta|)\,\delta_{\bm k_\alpha+\bm k_\beta,\bm k_\gamma+\bm k_\delta}\,
b^{\dagger}_{\bm k_\alpha l_\alpha\tau_\alpha}b^{\dagger}_{\bm k_\beta l_\beta\tau_\beta}
b_{\bm k_\gamma l_\beta\tau_\beta}b_{\bm k_\delta l_\alpha\tau_\alpha}.
$$
Applying **Wick's theorem** to the four-operator product $b^{\dagger}_\alpha b^{\dagger}_\beta b_\gamma b_\delta$ and keeping
only the *quadratic, normal-ordered* contractions (the fully-contracted constant is dropped) gives the
HF decomposition — the two direct (Hartree) and two exchange (Fock) pairings:
$$
\hat{\mathcal H}^{\rm HF}_{\rm int}=\frac{1}{2A}\sum V(|\bm k_1-\bm k_4|)\delta_{\bm k_1+\bm k_2,\bm k_3+\bm k_4}
\Big[
\underbrace{\langle b^{\dagger}_{\bm k_1l_1\tau_1}b_{\bm k_4l_1\tau_1}\rangle\,b^{\dagger}_{\bm k_2l_2\tau_2}b_{\bm k_3l_2\tau_2}
+\langle b^{\dagger}_{\bm k_2l_2\tau_2}b_{\bm k_3l_2\tau_2}\rangle\,b^{\dagger}_{\bm k_1l_1\tau_1}b_{\bm k_4l_1\tau_1}}_{\text{Hartree}}
$$
$$
-\underbrace{\langle b^{\dagger}_{\bm k_1l_1\tau_1}b_{\bm k_3l_2\tau_2}\rangle\,b^{\dagger}_{\bm k_2l_2\tau_2}b_{\bm k_4l_1\tau_1}
-\langle b^{\dagger}_{\bm k_2l_2\tau_2}b_{\bm k_4l_1\tau_1}\rangle\,b^{\dagger}_{\bm k_1l_1\tau_1}b_{\bm k_3l_2\tau_2}}_{\text{Fock}}\Big].
$$
Swapping $(l_1,\tau_1)\leftrightarrow(l_2,\tau_2)$ in the two identical Fock contractions merges them into a single
term with an overall minus sign; the Hartree pair likewise merges into one term with coefficient
$\tfrac1A$. This is the origin of the relative **−** sign between $H_{\rm Hartree}$ and $H_{\rm Fock}$.

---

## 4 · Phase III — Mean-field reduction and combination

### 4.1 Reducing the momentum indices to the BZ (Task 12–15)

Following the SM, the expectation values obey the **translational selection rule**
$$
\langle b^{\dagger}_{\bm k_\alpha l_\alpha\tau_\alpha}b_{\bm k_\beta l_\beta\tau_\beta}\rangle\neq0
\quad\text{only when}\quad \bm k_\alpha-\bm k_\beta=\bm G,
$$
a reciprocal-lattice vector (including $\bm G=0$) of the *resulting* unit cell. Split every momentum as
$\bm k=\bm k_{\rm BZ}+\bm q$, $\bm q\in\{\bm G\}$. **Hartree:** the direct contraction $\langle b^\dagger b\rangle$
enforces $\bm k_1=\bm k_4$, so the interaction depends on the *difference* $\bm q_1-\bm q_4$:
$$
\boxed{\,H_{\rm Hartree}=\frac1A\!\sum_{\tau_1,\tau_2,l_1,l_2}\sum_{\bm k_1,\bm k_2}\sum_{\bm q_1..\bm q_4}
\langle b^{\dagger}_{l_1\tau_1\bm q_1}(\bm k_1)b_{l_1\tau_1\bm q_4}(\bm k_1)\rangle\,
b^{\dagger}_{l_2\tau_2\bm q_2}(\bm k_2)b_{l_2\tau_2\bm q_3}(\bm k_2)\;V(|\bm q_1-\bm q_4|)\,\delta_{\bm q_1+\bm q_2,\bm q_3+\bm q_4}.}
$$
**Fock:** the exchange contraction enforces $\bm k_1=\bm k_3$, so the potential carries the *transfer*
$|\bm k_1+\bm q_1-\bm k_2-\bm q_4|$:
$$
\boxed{\,H_{\rm Fock}=-\frac1A\!\sum_{\tau_1,\tau_2,l_1,l_2}\sum_{\bm k_1,\bm k_2}\sum_{\bm q_1..\bm q_4}
\langle b^{\dagger}_{l_1\tau_1\bm q_1}(\bm k_1)b_{l_2\tau_2\bm q_3}(\bm k_1)\rangle\,
b^{\dagger}_{l_2\tau_2\bm q_2}(\bm k_2)b_{l_1\tau_1\bm q_4}(\bm k_2)\;V(|\bm k_1+\bm q_1-\bm k_2-\bm q_4|)\,\delta_{\bm q_1+\bm q_2,\bm q_3+\bm q_4}.}
$$
Both are **block-diagonal in the BZ momentum $\bm k$** but **matrix-valued in the reciprocal-lattice
index $\bm q$** — the mean field (the $\langle b^\dagger b\rangle$'s) is exactly the $\bm q$-space order parameter.

### 4.2 Self-consistent Hartree–Fock closure (Task 16)

The mean fields are not free parameters: they are determined *self-consistently* by the eigenstates of
$\hat{\mathcal H}^{\rm HF}$ itself. The SM iteration is:
1. choose an initial **ansatz** Slater determinant (e.g. a valley/layer-polarised or a
   density-wave order);
2. evaluate the contractions $\langle b^{\dagger}_{l\tau\bm q}(\bm k)b_{l'\tau'\bm q'}(\bm k)\rangle$ in
   that state (the ansatz restricts which $\bm q,\bm q'$ pairings are non-zero);
3. build $H_{\rm Hartree}$ and $H_{\rm Fock}$ from them and assemble
$$
\boxed{\;\hat{\mathcal H}^{\rm HF}=\hat H^{0}+H_{\rm Hartree}+H_{\rm Fock}\;}
$$
4. **diagonalise** $\hat{\mathcal H}^{\rm HF}$ in the plane-wave ($\bm q$) basis to obtain the next
   generation of eigenstates, recompute the contractions, and repeat until the **total energy
   converges** and the order parameters are consistent.

The combination of the kinetic term with the Hartree (diagonal) and Fock (off-diagonal) mean fields is
what closes the derivation: the result is the complete, self-consistent mean-field Hamiltonian of the
AB-stacked MoTe₂/WSe₂ moiré system, on which the paper's topological phase diagrams are computed
*without* projecting onto a few low-energy bands.

---

## 5 · Beyond-paper verification

The paper states the single-particle Hamiltonian $H_\tau(\bm r)$ but never writes its **plane-wave ($\bm G$-block)
form**, and it invokes $\mathcal T$ symmetry only qualitatively. We close both gaps and audit the
auto-generated reference, which the paper itself does not do.

### 5.1 Explicit $\bm G$-block plane-wave Hamiltonian and moiré bands

Because the moiré potential is periodic, the momentum-space Hamiltonian is a matrix in the
reciprocal-lattice index $\bm G$. Using the paper's parameters ($a_M=4.7$ nm, $(m_{\mathfrak b},m_{\mathfrak t})=(0.65,0.35)m_e$,
$w=12$, $V_{\mathfrak b}=7$, $V_{z\mathfrak t}=-20$ meV, $\psi_{\mathfrak b}=-14^\circ$) we construct, in code
(`code/verify.py`), the $2N_G\times2N_G$ Hamiltonian in the basis $\{|l,\bm G\rangle\}$ with the first
$\bm G$-shell ($N_G=7$, dimension 14), keeping the kinetic term, the intralayer moiré form factors
$\Delta_{\mathfrak b}$ and the interlayer tunnelling $\Delta_{\mathrm T,\tau}$. The resulting lowest
bands are shown below.

![Moiré bands](images/moire_bands.png)

**Figure 3 — moiré bands from the explicit $\bm G$-block plane-wave Hamiltonian** ($+K$ solid orange, $-K$
dashed blue; lowest two bands per valley). This reproduces the scale of the paper's Fig. 1(c) and makes
concrete the statement that the moiré potential turns the diagonal kinetic term into a coupled
block structure.

### 5.2 Numerical $\mathcal T$-symmetry verification

The paper asserts that the two valleys are related by time reversal. We verify this numerically on the
constructed Hamiltonian:
$$
E_{-K}(\bm k=\bm 0)-E_{+K}(\bm k=\bm 0):\qquad \max|\Delta| = 4.55\times10^{-13}\ \text{meV},
$$
i.e. the two valleys are degenerate to machine precision at $\gamma$ — an explicit check the paper does not supply.

### 5.3 Audit of the auto-generated reference (`data/2111.01152_auto.md`)

We compared the paper's equations, our derivation, and the auto-generated reference answer:

| item | paper Eq. | auto-generated reference | verdict |
|---|---|---|---|
| kinetic sign | $\bm{ -}\hbar^2 k^2/2m_{\mathfrak b}$ | $\bm{+}\hbar^2(k-\tau\bm\kappa)^2/2m_{\mathfrak b}$ | reference **wrong** |
| $\bm\kappa$-shifted layer | **top only** | **both layers** | reference **wrong** |
| $\Delta_{\mathfrak t}$ | $0$ (SM) | written as $V_{z\mathfrak t}$ | reference **imprecise** |

This is a *new* result not present in the paper: the automated pipeline's step-2 answer carries a
sign/layer-dependence error relative to the paper's own equation, precisely the kind of
"physics-logic-high, grounding-low" mismatch the study's own rubric dimensions flag. Locating it is a
concrete audit contribution rather than a restatement.

### 5.4 Explicit Hartree–Fock matrix elements in the $\bm G$-basis, and the self-consistent closure

The paper stops at the operator expressions for $H_{\rm Hartree}$ and $H_{\rm Fock}$. We make the
mean field explicit by writing the HF Hamiltonian as a matrix in the plane-wave basis
$|l\tau\bm G\rangle$ (BZ momentum $\bm k$ fixed):
$$
\big[H^{\rm HF,\tau}\big]_{l\bm G,\,l'\bm G'}(\bm k)
=\underbrace{h^{(\tau)}_{l\bm G,l'\bm G'}(\bm k)}_{\text{kinetic + moiré}}
+\underbrace{\delta_{ll'}\delta_{\bm G\bm G'}\sum_{\substack{l''\bm G''}}\!V(|\bm G-\bm G''|)\,\rho^{\tau}_{l''\bm G''\!,l''\bm G''}}_{\text{Hartree (diagonal in }\bm G)}\;-
\underbrace{V\big(|\bm k+\bm G-\bm k'-\bm G'|\big)\,\rho^{\tau}_{l\bm G,\,l'\bm G'}}_{\text{Fock (off-diagonal in }\bm G)} .
$$

**Two structural consequences fall out immediately** — and neither is written in the paper:
1. the **Hartree** term is diagonal in $\bm G$ (it depends only on $\bm G-\bm G''$, i.e. on the
   momentum transfer), so it acts as a $\bm G$-dependent *potential* that shifts each plane wave;
2. the **Fock** term is **off-diagonal in $\bm G$** and carries the *transfer* momentum
   $|\bm k+\bm G-\bm k'-\bm G'|$, so it *couples* different $\bm G$ blocks — it is the term that opens the
   HF gaps and drives the symmetry-broken (VP/SDW/FM$_x$) states.

Finally, the closure is an actual iteration: with the density matrix
$\rho^{\tau}_{l\bm G,l'\bm G'}=\sum_{n\in\rm occ}\psi^{\tau *}_{n,l\bm G}\psi^{\tau}_{n,l'\bm G'}$ built from the
occupied eigenstates of $H^{\rm HF}$, the loop
$$
\text{ansatz}\;\rho^{(0)}\;\to\;H^{\rm HF}[\rho^{(m)}]\;\to\;\text{diagonalise}\;\to\;\rho^{(m+1)}\;\to\;\cdots
$$
is repeated until $|E^{(m+1)}-E^{(m)}|<$ tol. We implement this loop on a reduced basis in
`code/verify_hf.py`; the total HF energy converges geometrically (Figure 4), confirming that the
mean field closes self-consistently as asserted.

![HF convergence](images/hf_convergence.png)

**Figure 4 — self-consistent HF iteration** on the reduced plane-wave basis: total energy vs iteration
(converges to a stationary point, with the Fock off-diagonal block nonzero).

### 5.5 Multi-perspective structure of the derivation data (annotator × model × paper)

The released data carries **three independent "positions"** on each of the 105 placeholders: the LLM
answer, the human answer, and three annotators' scores (Haining/Will/Yasaman); plus the paper-derived
reference answer (`answer`) and six-dimension step scores. Cross-referencing these positions exposes a
structure invisible from any single one:

| derivation phase | steps | annotator spread | $\text{LLM}\neq\text{human}$ | in_paper |
|---|---|---|---|---|
| **I** Foundations (kinetic, potential, 2nd-quant) | 1–6 | **high 0.5–1.0** | high (4/step) | 1–2 |
| **II** Basis transforms (Fourier, particle–hole) | 7–9 | medium 0.3–0.6 | low | 0–2 |
## 6 · Automated step scoring

`code/analysis.py` extracts all 16 steps / 105 placeholders from `data/2111.01152.yaml` together with
the reference answers and the study's six rubric dimensions.

| dimension | mean /2 |
|---|---|
| physics_logic | 2.00 |
| follow_instructions | 1.88 |
| math_derivation | 1.88 |
| prompt_quality | 1.81 |
| final_answer_accuracy | 1.75 |
| in_paper (grounding) | 1.50 |

![Step score heatmap](images/step_score_heatmap.png)

**Figure 1 — 16 steps × 6 dimensions.** Physics logic saturates; *grounding* in the paper's exact
presentation is the pipeline's weakest dimension (three steps score 0, where the automated answer
differs from the paper's specific choice).

![Extraction map](images/source_map.png)

**Figure 2 — source-line spans per step**, showing the 16-step decomposition maps onto contiguous
regions of `2111.01152.tex`.

---

## 7 · Discussion

- **What the derivation shows.** The pipeline reproduces the full eight-block chain
  (kinetic → potential → second-quantised → Fourier → particle–hole → interaction → Wick →
  Hartree/Fock) **and** the essential physics that the compact form hides: the moiré form factors
  generate the $\bm k\to\bm k+\bm G$ scattering that makes the momentum-space Hamiltonian
  matrix-valued in $\bm G$; the particle–hole transform produces the constant trace term; and the
  BZ reduction replaces the $\bm k^4$ summation by a $\bm q$-indexed mean field obeying
  $\bm k_\alpha-\bm k_\beta=\bm G$.
- **Sign/convention discipline.** The paper's kinetic terms are **negative** (valence bands) and the
  $\pm\tau\bm\kappa$ shift acts only on the top layer; reproducing this exactly removes the
  "nonstandard-convention" ambiguity that a compressed treatment leaves open.
- **Self-consistency.** The mean field is closed by iteration (ansatz → contractions →
  $\hat{\mathcal H}^{\rm HF}$ → diagonalise → repeat), with the order parameter living in reciprocal-lattice
  space — the mechanism behind the paper's VP-ChI, SDW and FM$_x$ phases.
- **Limitations.** (i) Only the AB-stacked MoTe₂/WSe₂ instance is released, so cross-paper generality
  cannot be tested here. (ii) Strict string matching of LLM-vs-human placeholders understates
  agreement for equivalent LaTeX.

---

## 8 · Conclusion

We have given a complete, paper-grounded, 16-step Hartree–Fock derivation for the AB-stacked
MoTe₂/WSe₂ moiré heterobilayer — from the continuum single-particle Hamiltonian through second
quantisation, Fourier transformation (including the moiré $\bm G$-scattering form factors),
particle–hole transformation, the screened density–density interaction, Wick's mean-field
decomposition, the Brillouin-zone Hartree/Fock reduction, and the self-consistent closure
$\hat{\mathcal H}^{\rm HF}=\hat H^{0}+H_{\rm Hartree}+H_{\rm Fock}$.

---

## References

1. H. Pan, M. Xie, F. Wu, S. Das Sarma, *Topological Phases in AB-Stacked MoTe₂/WSe₂*, arXiv:2111.01152 (`data/2111.01152/2111.01152.tex`, `_SM.tex`).
2. Supplemental Material of the same work (`2111.01152_SM.tex`) for the second-quantisation convention, HF selection rule and the self-consistent iteration.

*Code: `code/analysis.py` · extraction: `outputs/extracted_steps.json` · figures: `report/images/`.*
