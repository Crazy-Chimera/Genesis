# GENESIS-2.24 — Rule-Native Cross-Seed Screening

## Protocol

GENESIS-2.24 tests a representation derived directly from the universe rule variables rather than observer-defined region coordinates.

- Seeds: 390001–390006
- 500 ticks per seed
- Leave-one-seed-out evaluation
- Training: five source seeds
- Target: one unseen seed
- Target: next coherence innovation
- Primary baseline: zero-change
- Control: shuffled representation

## Verified result

- Workflow: PW-001 GENESIS-2.24 rule-native screening
- Run: #1
- Commit: cbf7f8ad7bc235ede5ab741afca31aa034ff6d00
- Artifact: 11309273234
- Artifact digest: sha256:21bb12c5ac4c304f1045dbea2d247950ca7c1b60f8f2679b8da8d5fe97b6f4f8
- CI benchmark job: SUCCESS

| Target seed | Samples | Zero MAE | Rule-native MAE | Shuffled MAE | Improvement |
|---:|---:|---:|---:|---:|---:|
| 390001 | 250 | 0.00000947308 | 0.000289259401 | 0.000289259401 | -0.000279786321 |
| 390002 | 250 | 0.000022792139 | 0.000025591166 | 0.000025591166 | -0.000002799027 |
| 390003 | 250 | 0.000003926005 | 0.000039383248 | 0.000039383248 | -0.000035457243 |
| 390004 | 250 | 0.000005700032 | 0.000037452841 | 0.000037452841 | -0.000031752809 |
| 390005 | 250 | 0.000009748586 | 0.000033624056 | 0.000033624056 | -0.000023875470 |
| 390006 | 250 | 0.000007548743 | 0.000006438879 | 0.000006438879 | +0.000001109864 |

## Decision

- Cases: 6
- Beats zero-change: 1/6
- Beats shuffled: 2/6
- Mean improvement: -0.0000620935011
- Decision: negative

The rule-native representation does not establish a cross-seed predictive mechanism. In particular, its shuffled control is identical to the rule-native MAE in the reported cases, so the test does not provide evidence that the observed performance is exploiting temporal ordering in the representation.

## Consequence

The negative result is important because it tests the hypothesis that seed-specific observer coordinates were the main limitation. Under this screening protocol, moving closer to the underlying universe rule did not produce robust predictive generalization.

The measurement-only invariants remain intact: no universe rule was modified, no prediction was fed back, and no goals, rewards, agency, self-model, or Agent Ω semantics were introduced.

## Next question

GENESIS should now avoid simply adding more feature dimensions. The next useful experiment is a pre-registered analysis of **rule-level invariants**: quantities analytically tied to the local update equation, evaluated across seeds with the same zero-change and shuffled controls. A positive result should require held-out baseline superiority, shuffled superiority, and cross-seed consistency.
