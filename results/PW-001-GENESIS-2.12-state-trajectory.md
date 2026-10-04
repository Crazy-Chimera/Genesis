# GENESIS-PW-001 — GENESIS-2.12 State-Trajectory Result

## Protocol

GENESIS-2.12 tests whether a short trajectory of **non-coherence state** can predict the next coherence innovation.

Input:
- consecutive observer states
- combined non-coherence state representation
- 193 dimensions per state
- history lengths 2, 3, 5, 10

Target:
- next coherence innovation: ΔC = C(t+1) − C(t)

Controls:
- zero-change baseline
- deterministic shuffled trajectory control

The universe rules are unchanged. Coherence history is not supplied to the predictor.

## Reproducibility

Workflow run: #79  
Run ID: 37120009584  
Commit: 4f116b5956f045ca9adc0f53f42c597572bdc889  
Artifact ID: 11273517588  
Artifact SHA-256: 6ce5ebb2f745e392b440cb99db5e660d7e35aa61a0b70d6bef2d7937acaffc5c

CI result: SUCCESS.

Seeds:
- 390001
- 390002
- 390003

## Results

| Seed | History | Samples | Zero MAE | Trajectory MAE | Shuffled MAE | Improvement |
|---|---:|---:|---:|---:|---:|---:|
| 390001 | 2 | 103839 | 0.000120512 | 0.000201675 | 0.000275122 | -0.000081163 |
| 390001 | 3 | 103793 | 0.000120483 | 0.001072696 | 0.001145939 | -0.000952213 |
| 390001 | 5 | 103701 | 0.000120425 | 0.002187077 | 0.002259640 | -0.002066651 |
| 390001 | 10 | 103471 | 0.000120283 | 0.005539295 | 0.005608233 | -0.005419012 |
| 390002 | 2 | 93912 | 0.000097226 | 0.000212087 | 0.000238876 | -0.000114861 |
| 390002 | 3 | 93873 | 0.000097194 | 0.000511076 | 0.000537939 | -0.000413881 |
| 390002 | 5 | 93795 | 0.000097132 | 0.000952413 | 0.000978786 | -0.000855281 |
| 390002 | 10 | 93600 | 0.000096976 | 0.002518024 | 0.002543455 | -0.002421048 |
| 390003 | 2 | 86895 | 0.000107082 | 0.000271723 | 0.000309762 | -0.000164642 |
| 390003 | 3 | 86853 | 0.000107062 | 0.000689745 | 0.000741134 | -0.000582683 |
| 390003 | 5 | 86769 | 0.000107024 | 0.001359063 | 0.001410540 | -0.001252039 |
| 390003 | 10 | 86559 | 0.000106930 | 0.002842450 | 0.002900076 | -0.002735520 |

## Interpretation

### Primary result

The state trajectory **does not beat the zero-change baseline in any tested condition**.

Therefore GENESIS-2.12 does **not** establish predictive information sufficient for this linear trajectory model.

### Secondary result

The trajectory predictor beats the shuffled control in all 12 conditions.

This means the ordered trajectory is not equivalent to a random permutation: temporal ordering contains measurable structure. However, that structure is not being converted into useful next-innovation prediction by the current model.

### Scientific status

GENESIS-2.12 is a **negative result for the tested predictor**, not evidence that no predictive information exists in the state trajectory.

The distinction is important:

1. ordered state trajectories contain structure;
2. the current 193-D linear ridge trajectory model fails to exploit it;
3. therefore the next experiment should test whether the limitation is representational/model-class related before claiming absence of predictive information.

## Decision

GENESIS-2.12 is closed.

Do not activate:
- self-model
- endogenous memory
- goals/reward
- agency
- recursive self-modification

The observer remains external and measurement-only.

## Next experiment

GENESIS-2.13 should isolate the source of failure rather than simply increasing model complexity.

Priority:
1. normalize trajectory features by first differences / per-feature temporal change;
2. compare state-difference trajectory against raw-state trajectory;
3. use a low-dimensional temporal model before another high-dimensional combination;
4. preserve chronological holdout and shuffled controls;
5. require robustness across all three seeds.

A positive result should require beating the zero-change baseline, not merely beating shuffled data.
