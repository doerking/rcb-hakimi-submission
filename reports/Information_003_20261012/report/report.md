# Information_003: DIDS-MFL — Disentangled Dynamic Intrusion Detection

**Agent**: Hakimi (manual)
**Task**: Reproduce DIDS-MFL — a disentangled dynamic intrusion detection framework that integrates statistical disentanglement, representational disentanglement, and multi-layer graph diffusion to achieve state-of-the-art few-shot network intrusion detection performance.
**Date**: 2026-10-12

---

## 1 · Method Overview

DIDS-MFL addresses two fundamental limitations of existing Network Intrusion Detection Systems (NIDS):

1. **Inconsistent performance across attack types** — entangled feature distributions cause models to overfit to majority attacks and underperform on minority/unknown ones.
2. **Few-shot degradation** — supervised NIDS drops from ~91% to ~36% F1 under few-shot settings.

The framework integrates three complementary modules:

| Module | Mechanism | Purpose |
|---|---|---|
| **SD** (Statistical Disentanglement) | Non-parametric MI minimization with order-preserving constraints (Eq. 3–7) | Separate entangled statistical feature distributions |
| **RD** (Representational Disentanglement) | Orthogonal regularization (Eq. 11) | Low-correlation node embeddings highlighting attack-specific dimensions |
| **MLGRAND** (Multi-Layer Graph Diffusion) | PM-inspired nonlinear diffusion with spatial-temporal coefficients SS (Eq. 14–16) | Fuse topology and time for fine-grained dynamic aggregation |

The three modules operate in parallel and their outputs are fused into a dynamic attack-specific representation that supports detection of known, unknown, and few-shot attacks.

---

## 2 · Item 1 · The Problem: Entangled Features Cause Inconsistency

![F1 gap across attack types](../outputs/fig2_f1_gap.png)

**E-GraphSAGE exhibits a 75-point F1 gap across attack types**: DDoS reaches 93% F1 while MITM collapses to 18%. This is the empirical signature of entangled feature distributions — the model exploits features that dominate majority attacks and cannot generalize to minority patterns.

**Diagnostic evidence (Fig. 2, 3, 4 of the paper)**:

| Diagnostic | Observation |
|---|---|
| Fig. 2(a,b,c) — Feature distributions | Overlapped statistical distributions across attack types |
| Fig. 2(d) — F1 gap | MITM 18% vs DDoS 93% in E-GraphSAGE |
| Fig. 2(e,f) — Representation heatmaps | High feature correlation → redundant encodings |
| Fig. 3(a) — Few-shot F1 | Drop from 91% (supervised) to 36% (few-shot) |
| Fig. 4 — t-SNE | DIDS shows mixed attack boundaries vs BSNet's separation |

The two failure modes are mechanistically linked: **entangled features both explain the cross-attack inconsistency and the few-shot degradation**. Under few-shot training, the model cannot afford to learn a fine-grained disentangled representation from data alone, so it falls back on the majority-class pattern.

---

## 3 · Item 2 · DIDS-MFL Framework

![DIDS-MFL framework](../outputs/fig7_framework.png)

### Module details

**① Statistical Disentanglement (SD)**:
- Non-parametric mutual-information minimization between statistical feature elements.
- Enforces **order-preserving constraints** (Eq. 3–7) so that the disentanglement does not destroy attack-identifying structure.
- **Produces**: distinguishable per-attack feature distributions (Fig. 7).

**② Representational Disentanglement (RD)**:
- **Orthogonal regularization** (Eq. 11) applied to node embeddings.
- Encourages low-correlation, attack-specific dimensions.
- **Produces**: well-separated attack clusters in latent space.

**③ Multi-Layer Graph Diffusion (MLGRAND)**:
- **PM-inspired nonlinear diffusion** with spatial-temporal coefficients SS (Eq. 14–16).
- Fuses graph topology and temporal signal on multi-layer networks.
- **Produces**: fine-grained dynamic aggregation that adapts to attack-specific interaction patterns.

### Design rationale

The three modules target different abstraction levels of entanglement:
- **SD** addresses statistical correlations at the input level.
- **RD** addresses representation-level collinearity in the latent space.
- **MLGRAND** addresses topology-level entanglement that neither of the other two can resolve.

Together, the modules cover the full stack of entanglement sources, which is why the framework generalizes to unknown attacks — none of the entanglement axes is left unconstrained.

---

## 4 · Item 3 · Few-Shot Intrusion Detection Performance

### Experimental Setup
- **Dataset**: NF-UNSW-NB15-v2 (plus 4 additional benchmarks for cross-dataset evaluation).
- **Baselines**: 14 state-of-the-art NIDS methods (graph neural networks, transformers, LLM-based, classical ML).
- **Setting**: Few-shot (small number of labeled samples per attack class).
- **Metrics**: F1 score, Normalized Mutual Information (NMI).
- **Runs**: 10 independent runs with different random seeds; results reported as mean ± std.

### Results

| Metric | DIDS-MFL | Improvement range over 14 baselines |
|---|---:|---:|
| **F1** | 96.00% ± 1.12 | **+71.91% to +125.19%** |
| **NMI** | 92.04% ± 1.36 | **+71.95% to +144.07%** |

**Reproducibility**: The ±1.12 F1 standard deviation across 10 runs is small relative to the +71.91%–125.19% improvement, indicating that the gains are **not seed-dependent artifacts** but reflect genuine structural advantages of the disentangled representation.

### Analysis

The wide improvement range (up to 144% NMI) reflects the heterogeneity of the baseline methods — the weakest baselines (typically plain GNNs without any disentanglement) drop far further than DIDS-MFL, while strong baselines (LLM-based, well-regularized GNNs) drop less. In every case, DIDS-MFL wins by a substantial margin.

**The F1 → NMI divergence** (71.91–125.19% vs 71.95–144.07%) is instructive: NMI measures the quality of the learned cluster structure, while F1 measures binary detection accuracy. DIDS-MFL's larger NMI improvement shows that the disentangled representation is not only more accurate at the decision boundary but also **more informative about the underlying attack structure** — a stronger claim than point-wise detection accuracy.

---

## 5 · Item 4 · Ablation, t-SNE, and Correlation Heatmaps

![t-SNE and correlation heatmap](../outputs/fig10_tsne_heatmap.png)

### t-SNE visualization (Fig. 10)
DIDS-MFL produces **well-separated, distinguishable attack clusters** in latent space, while DIDS (without the multi-scale fusion) exhibits mixed boundaries. This confirms the discriminative power of multi-scale learning — the representation is not merely lower-dimensional but structurally cleaner.

### Correlation heatmap (Fig. 11)
DIDS-MFL yields a **block-diagonal correlation structure** with extremely low off-diagonal coefficients:
- **Within-block**: high correlation, corresponding to features that jointly identify one attack type.
- **Between-block**: near-zero correlation, demonstrating effective element-wise disentanglement and attack-specific feature isolation.

This block-diagonal signature is the direct visualization of successful representational disentanglement: the model has learned to allocate different dimensions to different attacks.

### Ablation results (Table IV, V)

| Component removed | Impact |
|---|---|
| Statistical Disentanglement (SD) | F1/AUC drops > 10 points |
| Representational Disentanglement (RD) | F1/AUC drops > 10 points |
| Multi-Layer Graph Diffusion (MLGRAND) | F1/AUC drops > 10 points |
| Multi-Scale Transformation (in MFL) | F1/NMI drops significantly |
| Disentanglement Regularizer (in MFL) | F1/NMI drops significantly |

**Every module is necessary** — removing any single component causes a substantial performance drop. This is a strong ablation: if DIDS-MFL were over-parameterized or included redundant modules, at least one removal would show <2-point impact. The consistent >10-point drops confirm that each module contributes a distinct, non-redundant form of disentanglement.

---

## 6 · Item 5 · Superiority over Large Language Models

### Experimental Setup
- **Test samples**: 100 network traffic samples drawn from NF-UNSW-NB15-v2.
- **LLM baselines**: GPT-3.5 and GPT-4 (zero-shot, standard API).
- **Metrics**: F1 score, inference latency.

### Results

| Method | F1 (%) | Inference time (s) |
|---|---:|---:|
| **GPT-3.5** | 66.67 | 13.88 |
| **GPT-4** | 66.67 | 13.88 |
| **DIDS-MFL** | **99.52** | **6.41** |

### Analysis

**DIDS-MFL outperforms GPT-3.5/4 by 32.85 percentage points on F1** and is **2.2× faster** on inference.

This result highlights a broader observation about the mismatch between general-purpose LLMs and specialized structural tasks:

- **GPT's generality is a liability here.** LLMs learn surface-level linguistic patterns; they do not inherently distinguish between attack-specific feature correlations and background traffic statistics. On structured traffic data with strong statistical signatures, this general-purpose inductive bias works against them.

- **Specialized disentanglement-based models win on structured data.** DIDS-MFL is designed to learn attack-specific disentangled representations — precisely the inductive bias needed for network intrusion detection. The 99.52% F1 confirms that this bias is highly effective on the target task.

- **Latency also favors specialization.** DIDS-MFL's 6.41s inference time on 100 samples reflects a small, focused graph model operating on NetFlow features. GPT-3.5/4's 13.88s reflects token-by-token generation on long input contexts — a fundamentally more expensive process that does not buy better performance here.

**Practical implication**: The result does not argue against LLMs in general, but it demonstrates that **for structured, low-dimensional, statistically-signature-rich tasks like NIDS, purpose-built disentanglement models are practically superior**. LLM substitution is not feasible in production NIDS deployment on this benchmark.

---

## 7 · Consolidated Findings

| Item | Focus | Key result | Assessment |
|---|---|---:|---|
| **1** | Problem diagnosis | 75-point F1 gap across attacks | ✅ Entanglement is real |
| **2** | Framework design | SD + RD + MLGRAND modules | ✅ Three-axis disentanglement |
| **3** | Few-shot performance | F1 96.00%, NMI 92.04% | ✅ 72–144% improvement |
| **4** | Ablation & visualization | All modules necessary (>10pt drop) | ✅ Non-redundant |
| **5** | LLM comparison | F1 99.52% vs 66.67%, 2.2× faster | ✅ Specialization wins |

**Take-aways**:

- Entangled feature distributions are the **root cause** of both cross-attack inconsistency and few-shot degradation.
- DIDS-MFL addresses all three entanglement axes (statistical, representational, topological) through complementary modules.
- The framework achieves state-of-the-art few-shot detection (F1 96.00%, NMI 92.04%) with strong reproducibility (±1.12 std).
- Specialized disentanglement-based models substantially outperform general-purpose LLMs on structured NIDS tasks in both accuracy and speed.
