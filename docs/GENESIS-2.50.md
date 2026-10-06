# GENESIS-2.50 — Coupling Noise Amplitude Sweep

## Question

How does stochastic noise amplitude affect the local coupling-estimation offset identified in GENESIS-2.48 and attributed to noise in GENESIS-2.49?

## Protocol

Actual coupling values: `0.0025`, `0.01`, `0.02`.

Noise amplitudes: `0`, `0.00025`, `0.0005`, `0.001`, `0.002`.

For each condition, the predictor evaluates the actual coupling and adjacent candidates at `±0.000125`.

The predictor is external. No prediction is fed back into `GenesisUniverse`.

## Reproduction

Workflow: `GENESIS-2.50 coupling noise sweep`

Entry point: `experiments/pw001_coupling_noise_sweep.py`

The workflow evaluates 15 seed × noise × coupling conditions and stores the raw output as an artifact.

## Interpretation rule

The experiment is not considered positive merely because a noisy condition selects the exact coupling. The primary quantities are exact-recovery frequency, signed grid offset, prediction MAE, and their dependence on noise amplitude.

A systematic dependence of the coupling-selection offset on noise amplitude would strengthen the attribution established in GENESIS-2.49. Absence of such dependence would constrain that interpretation.

The result remains an implementation-level property of the tested PW-001 computational rule. It is not evidence of intelligence, agency, self-modeling, endogenous learning, or a general physical law.

## Research frontier

After 2.50, the clean next step is to repeat the relationship on additional unseen seeds and finer coupling grids before treating the coupling minimum as a quantitative estimator.
