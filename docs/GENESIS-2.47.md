# GENESIS-2.47 — Controlled Coupling Perturbation

## Purpose

Test whether the mechanistic predictive relation identified in GENESIS-2.36–2.46 remains specifically tied to the configured PW-001 coupling value under controlled perturbation.

The predictor remains external and measurement-only. No prediction is fed back into the universe.

## Protocol

Six seeds: 390073–390078.

Coupling grid: 0, 0.0025, 0.005, 0.01, 0.015, 0.02.

For each seed, the benchmark searched for the coupling value producing the minimum mechanistic prediction MAE and compared it with the actual configured coupling.

## Verified result

Workflow: PW-001 experiment #282  
Artifact: 11393570195  
Artifact digest: sha256:35c127bed5b488ef9eb818a5dc5a67f7f326cdc29c129c6ffb49389fefd15111

**Matched: 6/6.**

| seed | actual coupling | best coupling | best MAE | zero-change MAE | matched |
|---:|---:|---:|---:|---:|:---:|
| 390073 | 0 | 0 | 3.45998583587102e-07 | 3.45998583587102e-07 | true |
| 390074 | 0.0025 | 0.0025 | 3.52258269250359e-07 | 1.19709842747515e-06 | true |
| 390075 | 0.005 | 0.005 | 3.58872608519264e-07 | 1.07212035891056e-06 | true |
| 390076 | 0.01 | 0.01 | 3.5437238687794e-07 | 3.26020569429648e-06 | true |
| 390077 | 0.015 | 0.015 | 3.61300377843137e-07 | 1.74470249333325e-06 | true |
| 390078 | 0.02 | 0.02 | 3.51665943727042e-07 | 9.00658409940717e-06 | true |

## Interpretation

The controlled perturbation reproduces the actual coupling value as the minimum-error value in every tested seed.

This is stronger than merely observing that coupling is useful: within the tested grid, the predictor identifies the coupling used by the corresponding universe.

The result remains limited to the tested computational rule, parameter grid, seeds, and prediction protocol. It does not establish a general physical law, intelligence, agency, self-modeling, or endogenous learning.

## Non-interference invariants

- Universe rules remain unchanged during prediction.
- The predictor is external.
- No prediction is fed back into GenesisUniverse.
- No endogenous memory is introduced.
- No goals or rewards are introduced.
- No agency or self-model is introduced.

## Research frontier

The next clean step is to increase resolution around the identified coupling values and test whether the result survives independently reproduced implementations and additional parameter perturbations, while keeping the falsification protocol explicit.