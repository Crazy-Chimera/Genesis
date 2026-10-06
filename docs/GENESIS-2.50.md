# GENESIS-2.50 — Coupling Noise Amplitude Sweep

## Question

How does stochastic noise amplitude affect the local coupling-estimation offset identified in GENESIS-2.48 and attributed to noise in GENESIS-2.49?

## Protocol

Actual coupling values: `0.0025`, `0.01`, `0.02`.

Noise amplitudes: `0`, `0.00025`, `0.0005`, `0.001`, `0.002`.

For each condition, the predictor evaluates the actual coupling and adjacent candidates at `±0.000125`.

The predictor is external. No prediction is fed back into `GenesisUniverse`.

## Verified result

Workflow: **GENESIS-2.50 coupling noise sweep #3 — SUCCESS**  
Commit: `c62eb86b1ab4d33ab92acc39dc8817c8eccbe548`  
Artifact: `11395841466`  
Artifact digest: `sha256:3eab69d470b1cd4c0a4b89c1bbe083508d1ce472c480789faed8d19d27dcb8b0`  
Conditions: **15/15** completed.

| noise | exact recoveries | offsets |
|---:|---:|---|
| 0 | 3/3 | all 0 |
| 0.00025 | 3/3 | all 0 |
| 0.0005 | 3/3 | all 0 |
| 0.001 | 2/3 | one −0.000125 |
| 0.002 | 2/3 | one +0.000125 |

The mean MAE rises with noise amplitude in the tested conditions. The only coupling-selection errors are one grid step from the actual coupling; no case selects a value farther from the actual coupling.

### Interpretation

The result strengthens the GENESIS-2.49 attribution: increasing stochastic noise raises the prediction residual and eventually produces small one-grid-step coupling-selection offsets. The effect is bounded at the tested resolution and does not imply that the underlying coupling has changed.

This is an implementation-level attribution result for the tested PW-001 computational rule. It does not establish intelligence, agency, self-modeling, endogenous learning, or a general physical law.

## Reproduction

Workflow: `GENESIS-2.50 coupling noise sweep`

Entry point: `experiments/pw001_coupling_noise_sweep.py`

The raw result is stored in artifact `11395841466`.

## Research frontier after 2.50

The next clean control is **replication across additional unseen seeds at the same noise amplitudes**, followed by a finer coupling grid around the local minimum. The purpose is to determine whether the one-grid-step offsets remain bounded and whether their frequency scales reproducibly with noise amplitude.
