# GENESIS-2.53 — Coupling-Offset Bootstrap Uncertainty

## Question

Does the coupling-selection offset observed in GENESIS-2.48–2.52 remain distinguishable from finite-sample variation when uncertainty is estimated by bootstrap?

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

Each noise × coupling condition contains 30 evaluations.

The reported quantities are:

- mean signed coupling offset;
- 95% bootstrap confidence interval;
- mean absolute offset;
- positive-offset rate;
- negative-offset rate.

## Verified result

Workflow: **GENESIS-2.53 coupling offset bootstrap #2 — SUCCESS**

Commit:

`31821f7d60c581b30376009b607f3ca21635c736`

Artifact:

`11403242053`

Artifact digest:

`sha256:490edead69a62464a6634f4abdbb4293f1e32caa9d7f6a9ed13d48ddb3e6bbb4`

All 15 noise × coupling conditions completed with n=30.

### Bootstrap output

| noise | actual | mean offset | 95% CI | mean abs. offset |
|---:|---:|---:|---:|---:|
| 0 | 0.0025 | 0 | [0, 0] | 0 |
| 0 | 0.01 | 0 | [0, 0] | 0 |
| 0 | 0.02 | 0 | [0, 0] | 0 |
| 0.00025 | 0.0025 | 0 | [0, 0] | 0 |
| 0.00025 | 0.01 | 0 | [0, 0] | 0 |
| 0.00025 | 0.02 | 0 | [0, 0] | 0 |
| 0.0005 | 0.0025 | 0 | [-0.0000125, 0.0000125] | 0.00000833 |
| 0.0005 | 0.01 | -0.00000417 | [-0.0000125, 0] | 0.00000417 |
| 0.0005 | 0.02 | 0 | [-0.0000125, 0.0000125] | 0.00000833 |
| 0.001 | 0.0025 | -0.000025 | [-0.0000458, -0.00000833] | 0.000025 |
| 0.001 | 0.01 | 0 | [-0.0000125, 0.0000125] | 0.00000833 |
| 0.001 | 0.02 | -0.0000125 | [-0.0000333, 0.00000833] | 0.0000292 |
| 0.002 | 0.0025 | 0.0000125 | [-0.0000208, 0.0000458] | 0.0000708 |
| 0.002 | 0.01 | 0.000025 | [-0.00000417, 0.0000542] | 0.0000583 |
| 0.002 | 0.02 | -0.00000417 | [-0.0000292, 0.0000208] | 0.0000375 |

## Interpretation

The bootstrap supports three bounded observations:

1. At noise 0 and 0.00025, all 90 evaluations recover the exact coupling value for every tested actual coupling.
2. At higher noise, small coupling-selection offsets appear, but they remain at or near the tested local grid resolution.
3. Several higher-noise confidence intervals include zero, so the bootstrap does not establish a non-zero systematic signed shift for every condition.

Thus GENESIS-2.53 strengthens the interpretation that the observed coupling offsets are associated with stochastic noise and finite grid selection rather than a deterministic change of the underlying coupling rule.

This is an implementation-level result for the specified PW-001 computational rule. It does not establish intelligence, agency, self-modeling, endogenous learning, or a general physical law.

## Next clean control

The next useful test is a finer coupling grid around the actual value, using the same replication structure. The purpose is to determine whether the observed one-grid-step offsets collapse toward zero as grid resolution increases.
