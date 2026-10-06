# GENESIS-2.52 — Statistical Coupling/Noise Offset Replication

## Question

Does the coupling-minimum offset observed in GENESIS-2.48–2.51 scale reproducibly with the amplitude of the production noise term?

## Protocol

Actual coupling values are 0.0025, 0.01, and 0.02. For each actual value, the predictor compares the exact coupling with adjacent candidates at ±0.000125.

Noise amplitudes are:

- 0
- 0.00025
- 0.0005
- 0.001
- 0.002

Each noise × coupling condition is replicated 30 times, for 450 total evaluations.

Reported statistics per condition:

- exact-match rate;
- mean absolute coupling offset;
- mean signed coupling offset;
- fraction of negative offsets;
- fraction of positive offsets.

The predictor remains external and no prediction is fed back into GenesisUniverse.

## Status

Implementation committed to `main` in:

`b42110678eb8b5628de63e900814f4d5bb850a7d`

Workflow:

`.github/workflows/genesis-2.52.yml`

The empirical result must be recorded only after the GitHub Actions run completes successfully and its artifact has been inspected.

## Research purpose

GENESIS-2.49 showed that removing noise eliminated the small coupling-grid offsets.

GENESIS-2.51 replicated the effect across five replicates per condition and showed that offset frequency increases at higher noise amplitudes.

GENESIS-2.52 increases replication to 30 per condition so that the noise-to-offset relationship can be summarized statistically rather than by a small number of individual trajectories.

This remains an implementation-level validation of the specified PW-001 computational rule. It does not establish intelligence, agency, self-modeling, endogenous learning, or a general physical law.
