# GENESIS-2.12 — State-Trajectory Benchmark

**Status:** completed; negative result  
**Experiment workflow:** PW-001 run #79  
**Run ID:** 37120009584  
**Commit:** 4f116b5956f045ca9adc0f53f42c597572bdc889  
**Artifact digest:** `sha256:6ce5ebb2f745e392b440cb99db5e660d7e35aa61a0b70d6bef2d7937acaffc5c`

## Question

Can a short trajectory of non-coherence state vectors predict the next coherence innovation, without using coherence history as input?

## Protocol

- Seeds: 390001, 390002, 390003.
- 10,000 universe steps per seed.
- Feature representation: 193-dimensional `combined_state`.
- History lengths: 2, 3, 5, 10.
- Chronological 50% holdout; consecutive ticks required.
- Ridge regression with coefficient 1e-6.
- Target: next coherence minus the last coherence in the input window.
- Baselines: zero-change predictor and shuffled state-trajectory control.
- Universe rules were not changed. The predictor remained an external observer.

## Results

All 12 tested seed × history-length combinations failed to beat the zero-change baseline. All 12 beat the shuffled control, which indicates some ordering sensitivity but not useful predictive accuracy under the chosen target and metric.

| Seed | History | Samples | Zero-change MAE | Trajectory MAE | Shuffled MAE | Improvement |
|---:|---:|---:|---:|---:|---:|---:|
| 390001 | 2 | 103839 | 0.0001205119 | 0.0002016748 | 0.0002751225 | -0.0000811628 |
| 390001 | 3 | 103793 | 0.0001204830 | 0.0010726959 | 0.0011459386 | -0.0009522129 |
| 390001 | 5 | 103701 | 0.0001204254 | 0.0021870771 | 0.0022596399 | -0.0020666517 |
| 390001 | 10 | 103471 | 0.0001202832 | 0.0055392949 | 0.0056082327 | -0.0054190117 |
| 390002 | 2 | 93912 | 0.0000972257 | 0.0002120865 | 0.0002388764 | -0.0001148609 |
| 390002 | 3 | 93873 | 0.0000971941 | 0.0005110756 | 0.0005379387 | -0.0004138815 |
| 390002 | 5 | 93795 | 0.0000971318 | 0.0009524127 | 0.0009787861 | -0.0008552810 |
| 390002 | 10 | 93600 | 0.0000969763 | 0.0025180244 | 0.0025434549 | -0.0024210481 |
| 390003 | 2 | 86895 | 0.0001070816 | 0.0002717234 | 0.0003097615 | -0.0001646418 |
| 390003 | 3 | 86853 | 0.0001070623 | 0.0006897452 | 0.0007411344 | -0.0005826828 |
| 390003 | 5 | 86769 | 0.0001070238 | 0.0013590625 | 0.0014105396 | -0.0012520387 |
| 390003 | 10 | 86559 | 0.0001069297 | 0.0028424499 | 0.0029000767 | -0.0027355202 |

## Interpretation

The 2.12 hypothesis is **not supported** under this protocol. Longer input trajectories substantially worsen held-out MAE. Beating the shuffled control is insufficient: the model must also beat the simple zero-change baseline.

This does not falsify the earlier GENESIS-2.9 result. It shows that the innovation signal found from coherence-history features has not been reconstructed from the current 193-dimensional non-coherence state trajectory.

## Decision for GENESIS-2.13

Do not add more state features to the same high-dimensional linear trajectory model yet. First isolate the information source with a controlled diagnostic:

1. Keep the universe and all observer rules fixed.
2. Compare current coherence, coherence history, non-coherence state, and shuffled controls in one shared split.
3. Add a low-dimensional baseline using only first differences of selected non-coherence features.
4. Report MAE and improvement against zero-change per seed, not only aggregate ordering effects.
5. Treat the probe as observer-only; no feedback, goals, endogenous learning, self-model, or AGI claims.

The next decision depends on whether the low-dimensional diagnostic recovers a robust signal. If it does not, record the negative result and stop feature expansion rather than tuning against the holdout.
