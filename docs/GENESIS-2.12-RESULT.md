# GENESIS-2.12 — State-Trajectory Benchmark

## Protocol

Predict the next coherence innovation

`ΔC(t+1) = C(t+1) - C(t)`

from a consecutive trajectory of the **combined non-coherence state**.

The predictor receives only the 193-dimensional observer state:

- structure: 5
- local patch: 9
- phase patch: 18
- gradient patch: 18
- motion: 3
- boundary flux: 5
- spatial field: 18
- multiscale field: 68
- relational: 16
- graph-relational: 33

Total: 193 features per frame.

Coherence history is excluded from the predictor input.

Controls:

- zero-change baseline
- deterministic shuffled trajectory control

Chronological 50% holdout; exact consecutive ticks required; ridge regression.

## Result

Run: PW-001 #79  
Commit: `4f116b5956f045ca9adc0f53f42c597572bdc889`  
Artifact: `pw001-predictive-results`  
Artifact digest: `sha256:6ce5ebb2f745e392b440cb99db5e660d7e35aa61a0b70d6bef2d7937acaffc5c`

| Seed | History | Samples | Zero MAE | Trajectory MAE | Shuffled MAE | Improvement |
|---:|---:|---:|---:|---:|---:|---:|
| 390001 | 2 | 103839 | 0.000120512 | 0.000201675 | 0.000275122 | -0.000081163 |
| 390001 | 3 | 103793 | 0.000120483 | 0.001072696 | 0.001145939 | -0.000952213 |
| 390001 | 5 | 103701 | 0.000120425 | 0.002187078 | 0.002259640 | -0.002066652 |
| 390001 | 10 | 103471 | 0.000120283 | 0.005539295 | 0.005608233 | -0.005419012 |
| 390002 | 2 | 93912 | 0.000097226 | 0.000212087 | 0.000238876 | -0.000114861 |
| 390002 | 3 | 93873 | 0.000097194 | 0.000511076 | 0.000537939 | -0.000413881 |
| 390002 | 5 | 93795 | 0.000097132 | 0.000952413 | 0.000978786 | -0.000855281 |
| 390002 | 10 | 93600 | 0.000096976 | 0.002518024 | 0.002543454 | -0.002421048 |
| 390003 | 2 | 86895 | 0.000107082 | 0.000271723 | 0.000309762 | -0.000164642 |
| 390003 | 3 | 86853 | 0.000107062 | 0.000689745 | 0.000741134 | -0.000582683 |
| 390003 | 5 | 86769 | 0.000107024 | 0.001359063 | 0.001410539 | -0.001252039 |
| 390003 | 10 | 86559 | 0.000106930 | 0.002842450 | 0.002900077 | -0.002735521 |

## Interpretation

The trajectory predictor **does not beat the zero-change baseline in any of the 12 tests**.

It **does beat the shuffled control in all 12 tests**.

Therefore the current evidence supports the narrower statement:

> The non-coherence state trajectory contains ordered information, but the present 193-dimensional linear trajectory model does not reconstruct next coherence innovation robustly.

This is a negative result for GENESIS-2.12, not evidence of intelligence, agency, self-modeling, or endogenous learning.

## Decision

Do not activate memory, goals, self-model, or Agent Ω.

Do not increase model complexity without a control.

The next probe is **GENESIS-2.13: compressed state trajectory**:

1. fit dimensionality reduction on the training half only;
2. test low-dimensional state trajectories;
3. keep the same seeds, holdout, consecutive-tick rule, zero baseline, and shuffled control;
4. compare whether compression removes high-dimensional overfitting while preserving ordered predictive information.

A positive result must beat zero-change across seeds and remain better than shuffled control. A negative result is also a valid outcome.
