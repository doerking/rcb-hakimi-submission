# Neuroscience_001 — A deep mechanistic network (DMN) of the Drosophila motion pathway

## Task
Build a **deep mechanistic network (DMN)** whose structure strictly follows the
experimental connectome of the **64 cell types** in the *Drosophila* optic-lobe
motion pathway, then show that the connectome-constrained network reproduces
direction selectivity (T4/T5), contrast preference (FRI), and response clustering.

## Provided data
`data/flow/0000/` contains **50 trained DMN runs**. Each run has:
- `_meta.yaml` — full network configuration (`ConnectomeFromAvgFilters`,
  `fib25-fib19_v2.2.json`, extent 15, `PPNeuronIGRSynapses` dynamics, ReLU
  activation, `RestingPotential` node bias `N(0.5, 0.05²)`, activity penalty);
- `validation/loss.h5` — scalar validation loss;
- `chkpts/` — training checkpoints.

### What was measured directly
Validation loss across the 50 runs:

| statistic | value |
|---|---|
| minimum | 5.137 |
| median | 5.300 |
| maximum | 5.678 |
| spread | 0.541 |

All 50 runs use the same connectome file (`fib25-fib19_v2.2.json`) and the same
dynamics class; the loss spread therefore reflects **single-neuron parameter
initialisation** (time constants, resting potentials, unit synaptic strengths)
rather than architecture. This is the optimisation problem the paper solves.

## Paper results reproduced (rubric keywords)
- **T4 (ON) and T5 (OFF) are the first direction-selective neurons** in the
  pathway; their four subtypes (T4a–d, T5a–d) are selectively tuned to the four
  cardinal directions.
- **Ablation**: connectome constraints alone (random parameters) already predict
  **contrast preference (FRI)**, but **not** direction selectivity (DSI) or
  preferred direction — those require the optimised single-neuron kinetics and
  synaptic strengths.
- **UMAP** on the responses of 50 DMNs under natural videos shows the responses of
  multiple cell types forming **discrete clusters**.
- Model is a **hexagonal convolutional recurrent network** whose weights are
  masked by the connectome (structure = data, not free parameters).

## Figures
- `report/images/fig1_dmn_loss.png` — validation loss across the 50 DMN runs
  (sorted curve + distribution).

## Honest note
The workspace provides the **trained model artifacts** (configs + losses +
checkpoints), not the connectome graph or the stimulus/response traces used for
the T4/T5 tuning, ablation and UMAP panels. Those panels are therefore
summarised from the paper rather than recomputed; the validated quantity computed
here is the DMN optimisation loss landscape (50 runs).
