# GENESIS-2.12 — State-Trajectory Benchmark

## Protocol

The predictor receives only a consecutive trajectory of the non-coherence observer state.

- Feature: combined state, 193 dimensions.
- Components: structure, local patch, phase patch, gradient patch, motion, boundary flux, spatial field, multiscale field, relational state, graph-relational state.
- History lengths: 2, 3, 5, 10.
- Target: next coherence innovation, `ΔC = C(t+1) - C(t)`.
- Coherence is excluded from the predictor input.
- Chronological 50% train/holdout split.
- Ridge regression.
- Exact consecutive-tick requirement.
- Controls: zero-change baseline and deterministic shuffled trajectory.

## Result

GENESIS-2.12 does **not** demonstrate predictive reconstruction of coherence innovation from the raw state trajectory.

| Seed | History | Samples | Zero MAE | Trajectory MAE | Shuffled MAE | Improvement |
|---|---:|---:|---:|---:|---:|---:|
| 390001 | 2 | 103839 | 0.000120511918 | 0.000201674753 | 0.000275122472 | -0.000081162836 |
| 390001 | 3 | 103793 | 0.000120482970 | 0.001072695877 | 0.001145938608 | -0.000952212907 |
| 390001 | 5 | 103701 | 0.000120425430 | 0.002187077128 | 0.002259639935 | -0.002066651698 |
| 390001 | 10 | 103471 | 0.000120283214 | 0.005539294907 | 0.005608232656 | -0.005419011694 |
| 390002 | 2 | 93912 | 0.000097225676 | 0.000212086546 | 0.000238876421 | -0.000114860870 |
| 390002 | 3 | 93873 | 0.000097194133 | 0.000511075599 | 0.000537938713 | -0.000413881465 |
| 390002 | 5 | 93795 | 0.000097131766 | 0.000952412740 | 0.000978786125 | -0.000855280973 |
| 390002 | 10 | 93600 | 0.000096976272 | 0.002518024373 | 0.002543454891 | -0.002421048101 |
| 390003 | 2 | 86895 | 0.000107081617 | 0.000271723428 | 0.000309761540 | -0.000164641811 |
| 390003 | 3 | 86853 | 0.000107062338 | 0.000689745169 | 0.000741134430 | -0.000582682831 |
| 390003 | 5 | 86769 | 0.000107023787 | 0.001359062524 | 0.001410539648 | -0.001252038737 |
| 390003 | 10 | 86559 | 0.000106929724 | 0.002842449886 | 0.002900076743 | -0.002735520163 |

## Interpretation

All 12 trajectory models have negative improvement relative to the zero-change baseline. Therefore the experiment does not support the claim that concatenated raw observer-state trajectories predict the next coherence innovation.

At the same time, every trajectory model beats its shuffled control. This indicates that temporal ordering contains measurable structure, but the tested linear representation fails to extract a useful next-step ΔC predictor.

This is a negative result for the **specific 2.12 representation**, not evidence that no predictive structure exists.

## Boundary

No universe rule was changed. The observer remains external. The predictor has no feedback path, no goal, no reward, no endogenous learning, and no self-model.

## Next probe

GENESIS-2.13 should test **state-change representation** rather than concatenated state levels: temporal differences of the non-coherence state (`S(t)-S(t-1)`) as predictors of the next coherence innovation. This directly tests whether the relevant signal is encoded in the *change of structure* rather than its absolute state.
