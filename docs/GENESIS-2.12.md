# GENESIS-2.12 — State-Trajectory Benchmark

## Purpose

Test whether a short consecutive trajectory of observer-derived, non-coherence state vectors can predict the next coherence innovation.

The universe rules are unchanged. Coherence history is excluded from the predictor input.

## Protocol

- Seeds: 390001, 390002, 390003
- State representation: combined observer state, 193 dimensions
- History lengths: 2, 3, 5, 10
- Target: next coherence innovation
- Train/test split: chronological 50%
- Consecutive ticks required
- Model: standardized linear ridge regression
- Baseline: zero-change prediction
- Control: deterministic shuffled test trajectories

## Results

| Seed | History | Samples | Zero MAE | Trajectory MAE | Shuffled MAE | Improvement |
|---:|---:|---:|---:|---:|---:|---:|
| 390001 | 2 | 103839 | 0.000120512 | 0.000201675 | 0.000275122 | -0.000081163 |
| 390001 | 3 | 103793 | 0.000120483 | 0.001072696 | 0.001145939 | -0.000952213 |
| 390001 | 5 | 103701 | 0.000120425 | 0.002187077 | 0.002259640 | -0.002066651 |
| 390001 | 10 | 103471 | 0.000120283 | 0.005539295 | 0.005608233 | -0.005419012 |
| 390002 | 2 | 93912 | 0.000097226 | 0.000212087 | 0.000238876 | -0.000114861 |
| 390002 | 3 | 93873 | 0.000097194 | 0.000511076 | 0.000537939 | -0.000413881 |
| 390002 | 5 | 93795 | 0.000097132 | 0.000952413 | 0.000978786 | -0.000855281 |
| 390002 | 10 | 93600 | 0.000096976 | 0.002518024 | 0.002543455 | -0.002421048 |
| 390003 | 2 | 86895 | 0.000107082 | 0.000271723 | 0.000309762 | -0.000164642 |
| 390003 | 3 | 86853 | 0.000107062 | 0.000689745 | 0.000741134 | -0.000582682 |
| 390003 | 5 | 86769 | 0.000107024 | 0.001359063 | 0.001410540 | -0.001252039 |
| 390003 | 10 | 86559 | 0.000106930 | 0.002842450 | 0.002900077 | -0.002735520 |

## Outcome

### Primary criterion

FAIL: state trajectory did not beat the zero-change baseline in any of the 12 seed/history combinations.

Therefore GENESIS-2.12 does not provide evidence that the tested 193-dimensional state trajectory is a useful predictor of next coherence innovation under this model and protocol.

### Control criterion

PASS: trajectory MAE was below shuffled MAE in all 12 combinations.

This means the chronological state trajectory contains some order-sensitive information relative to the shuffled control. However, that information was not successfully converted into predictive accuracy by the tested linear ridge model.

This distinction is important:

ordered signal != demonstrated predictive utility

## Interpretation

GENESIS-2.12 should be recorded as a negative predictive result, not as an emergence success.

The result also constrains the next experiment. Increasing trajectory length alone is not justified: performance deteriorates strongly as history grows from 2 to 10.

The next probe should therefore change the representation or predictive mechanism, rather than simply increasing history length.

## Recommended GENESIS-2.13 hypothesis

Test whether the observer state contains predictive information in a low-dimensional temporal representation rather than in the raw concatenated 193-dimensional trajectory.

Candidate protocol:

1. Keep the universe unchanged.
2. Keep coherence excluded from predictor input.
3. Compress each state vector into deterministic temporal invariants.
4. Test first differences and second differences of state features.
5. Compare current state, delta-state, second-difference state, and short temporal summaries.
6. Use the same chronological holdout and shuffled control.
7. Require improvement over zero-change across all three seeds before treating the result as robust.

No AGI, agency, self-model, endogenous learning, or causal emergence claim follows from this experiment.

## Reproducibility

Workflow run: 37120009584

Commit: 4f116b5956f045ca9adc0f53f42c597572bdc889

Artifact: 11273517588

Artifact digest: sha256:6ce5ebb2f745e392b440cb99db5e660d7e35aa61a0b70d6bef2d7937acaffc5c

The CI job completed successfully and explicitly executed experiments/pw001_state_trajectory.py.
