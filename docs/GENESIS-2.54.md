# GENESIS-2.54 — Fine-Grid Coupling-Offset Control

## Question

Does the small coupling-selection offset observed in GENESIS-2.53 remain when the local candidate grid is refined to a spacing of **0.0000625**?

## Protocol

Actual coupling values:

- 0.0025
- 0.01
- 0.02

Noise amplitudes:

- 0
- 0.00025
- 0.0005
- 0.001
- 0.002

Each condition contains **30 independent evaluations**. The candidate set is the actual coupling and its nearest grid neighbors at ±0.0000625.

Reported quantities:

- mean signed offset;
- 95% bootstrap confidence interval;
- mean absolute offset;
- positive/negative selection rates.

## Verified result

Workflow: **GENESIS-2.54 fine-grid coupling control #1 — SUCCESS**

Commit: `1e11d0316c8acf1cdc1574b6f59af24c8dc98fe6`

Artifact: `11403677416`

Artifact digest: `sha256:d9db59a7fab643f072e7555c3c5e7eec41a8af38e74f1f4667e49278af153688`

All **15/15** conditions completed with n=30.

## Results

| noise | actual | mean offset | 95% CI | mean abs. offset |
|---:|---:|---:|---:|---:|
| 0 | 0.0025 | 0 | [0, 0] | 0 |
| 0 | 0.01 | 0 | [0, 0] | 0 |
| 0 | 0.02 | 0 | [0, 0] | 0 |
| 0.00025 | 0.0025 | 0 | [-0.00000833, 0.00000833] | 0.00000833 |
| 0.00025 | 0.01 | 0.00000417 | [0, 0.0000104] | 0.00000417 |
| 0.00025 | 0.02 | -0.00000625 | [-0.0000146, 0] | 0.00000625 |
| 0.0005 | 0.0025 | 0.0000104 | [0, 0.0000208] | 0.0000146 |
| 0.0005 | 0.01 | -0.00000208 | [-0.0000104, 0.00000625] | 0.0000104 |
| 0.0005 | 0.02 | 0 | [-0.0000104, 0.0000104] | 0.0000125 |
| 0.001 | 0.0025 | -0.00000625 | [-0.0000229, 0.0000104] | 0.0000354 |
| 0.001 | 0.01 | -0.0000125 | [-0.0000271, 0.00000208] | 0.0000292 |
| 0.001 | 0.02 | 0.00000833 | [-0.00000625, 0.0000229] | 0.0000292 |
| 0.002 | 0.0025 | 0.00000417 | [-0.0000146, 0.0000229] | 0.0000417 |
| 0.002 | 0.01 | -0.00000208 | [-0.0000208, 0.0000146] | 0.0000396 |
| 0.002 | 0.02 | 0.00000625 | [-0.0000104, 0.0000229] | 0.0000396 |

## Interpretation

The result supports three bounded conclusions:

1. **Zero-noise control:** all 90 zero-noise evaluations recover the exact coupling.
2. **Noise dependence:** increasing noise produces small positive and negative coupling-selection offsets.
3. **No universal signed bias:** most higher-noise bootstrap intervals include zero, so the experiment does not establish a systematic non-zero signed shift.

The fine grid therefore does not reveal a stable deterministic displacement of the coupling minimum. The observed offsets remain compatible with stochastic selection at the tested resolution.

This is an implementation-level result for the specified PW-001 computational rule. It does not establish intelligence, agency, self-modeling, endogenous learning, or a general physical law.

## Next falsification target

The clean next experiment is to vary **grid spacing itself** while keeping the actual coupling and noise conditions fixed. The question is whether the absolute selection error scales with grid resolution as expected for a discretized estimator.

That test should report both:

- coupling-selection error versus grid spacing;
- noise × grid-spacing interaction.

The purpose is to distinguish a true parameter-selection effect from ordinary discretization plus stochastic noise.
