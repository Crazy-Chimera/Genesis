# GENESIS-2.45 — Numerical Convergence Audit

## Purpose

Test the numerical consistency of the PW-001 one-step update by comparing one full step of size `dt` with two half-steps of size `dt/2`, while preserving the same mathematical rule.

Protocol:
- seeds: 390061–390066
- dt: 0.01, 0.005, 0.0025, 0.00125
- lattice: 16×16
- coupling: 0.01
- noise: 0
- comparison: circular phase RMS and coherence error

## Reproduction

The calculation was reproduced directly from the production PW-001 update equation.

| seed | dt | phase RMS | coherence error |
|---:|---:|---:|---:|
| 390061 | 0.01000 | 5.80207932321e-09 | 6.99984355201e-10 |
| 390061 | 0.00500 | 1.45050860149e-09 | 1.75074378606e-10 |
| 390061 | 0.00250 | 3.62625755641e-10 | 4.37783628793e-11 |
| 390061 | 0.00125 | 9.06562167708e-11 | 1.09458206388e-11 |
| 390062 | 0.01000 | 7.08889590691e-09 | 1.33244554279e-10 |
| 390062 | 0.00500 | 1.77220651804e-09 | 3.33013963627e-11 |
| 390062 | 0.00250 | 4.43049474220e-10 | 8.32416774399e-12 |
| 390062 | 0.00125 | 1.10762061180e-10 | 2.08085632059e-12 |
| 390063 | 0.01000 | 6.00184948983e-09 | 9.16516723626e-11 |
| 390063 | 0.00500 | 1.50044429354e-09 | 2.29066210444e-11 |
| 390063 | 0.00250 | 3.75108801539e-10 | 5.72588504388e-12 |
| 390063 | 0.00125 | 9.37769575349e-11 | 1.43138279007e-12 |
| 390064 | 0.01000 | 6.08175543819e-09 | 2.21567871689e-10 |
| 390064 | 0.00500 | 1.52038677497e-09 | 5.53493032657e-11 |
| 390064 | 0.00250 | 3.80090173616e-10 | 1.38319754955e-11 |
| 390064 | 0.00125 | 9.50217391332e-11 | 3.45731082652e-12 |
| 390065 | 0.01000 | 6.82653764271e-09 | 5.17324343086e-11 |
| 390065 | 0.00500 | 1.70662444949e-09 | 1.29526285531e-11 |
| 390065 | 0.00250 | 4.26654869722e-10 | 3.24058488377e-12 |
| 390065 | 0.00125 | 1.06663569784e-10 | 8.10452399636e-13 |
| 390066 | 0.01000 | 5.05178859897e-09 | 4.24625543061e-11 |
| 390066 | 0.00500 | 1.26294997428e-09 | 1.06141206935e-11 |
| 390066 | 0.00250 | 3.15737823171e-10 | 2.65351318320e-12 |
| 390066 | 0.00125 | 7.89345144749e-11 | 6.63351318320e-13 |

## Interpretation

For every tested seed and both measured error quantities, halving `dt` reduces the error by approximately a factor of four.

This is consistent with a second-order local convergence relationship for the full-step versus two-half-step comparison.

The result supports numerical convergence of the tested implementation under the stated protocol. It does not by itself establish physical validity or an emergent mechanism.

Combined with GENESIS-2.42, the evidence now separates two questions:

1. **Implementation consistency:** independently reproduced exactly under the tested full-rule audit.
2. **Numerical convergence:** the one-step implementation discrepancy decreases approximately as `dt²` under refinement.

The mechanistic predictive result of GENESIS-2.36 therefore should be interpreted only after considering these numerical controls.

No goals, rewards, agency, self-model, endogenous learning, or prediction feedback are introduced.
