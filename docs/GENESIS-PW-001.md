# GENESIS-PW-001 — Primordial Emergence Experiment

## Purpose

Test whether persistent relational structures can emerge from local oscillator rules without hard-coding entities, language, goals, meaning, or intelligence.

## Universe

The GENESIS universe contains only oscillator state and local interaction rules. The observer is external and measurement-only.

### GENESIS-1.0

- 16x16 periodic lattice = 256 oscillators
- deterministic seed: 390001
- local four-neighbour coupling
- deterministic noise
- 100,000 ticks
- global coherence measurement

### GENESIS-1.1

The external observer adds a local coherence field and connected-region detection.

A detected coherent region is **not an entity**. It is an observer measurement. The universe does not store cluster labels and detection does not modify oscillator phases.

### GENESIS-1.2

The observer adds persistence, lifetime, boundary contrast, and Jaccard identity overlap.

Region identity is assigned by the observer using spatial overlap only. It is not part of the universe state.

### GENESIS-1.3

The observer adds a lifecycle event stream:

- **birth** — a measured region has no qualifying predecessor.
- **growth** — a tracked region gains cells.
- **decay** — a tracked region loses cells.
- **split** — one predecessor overlaps multiple current regions.
- **merge** — one current region overlaps multiple predecessors.
- **death** — a predecessor has no qualifying successor.

These are observer-level classifications of measured region sets. They are not causal mechanisms inside the universe.

### GENESIS-1.4

An external temporal memory records measured region observations and lifecycle events.

Each memory record contains:

- tick
- observer identity
- cells
- coherence
- boundary contrast
- lifetime
- persistence
- overlap
- lifecycle event kinds

TemporalMemory is append-only observer state. It does not write anything into GenesisUniverse, alter oscillator state, or create endogenous memory.

This layer is deliberately descriptive. Recording history does not imply that the universe itself remembers.

### GENESIS-1.5

An external predictive-memory layer evaluates whether temporal traces contain information about the next observed region state beyond a persistence baseline.

The baseline predicts that the next scalar feature remains equal to the most recent observation. The history predictor extrapolates a linear trend from a bounded history window. Prediction quality is measured with mean absolute error (MAE).

The predictor is measurement-only:

- it reads MemoryRecord values
- it does not modify GenesisUniverse
- it does not write back into TemporalMemory
- it does not introduce goals, rewards, agency, meaning, language, or self-models

A history-based predictor is considered empirically useful for this experiment only when its error is lower than the baseline on held-out transitions. This is a test of predictive information, not a claim of intelligence.
### GENESIS-1.5 empirical substrate experiment

The first direct experiment was run on the actual GENESIS-PW-001 substrate trajectory for ticks 0–10,000 using the same universe parameters and observer/tracker rules as the reference implementation.

For each observer-tracked identity, the experiment compared a persistence baseline with the linear history predictor over a three-record history window. The target was the next recorded observation for that identity. MAE was used as the error metric.

Observed result:

| feature | samples | persistence MAE | history MAE | improvement |
|---|---:|---:|---:|---:|
| coherence | 189,681 | 0.0001195000050 | 0.0000353671743 | +0.0000841328307 |
| region size | 189,681 | 0.000506112895 | 0.001012225790 | -0.000506112895 |

The trajectory produced 189,783 observer records across 102 observer-assigned identities during the 10,000-tick interval.

The result is feature-specific. Coherence contained measurable short-history predictive information under this predictor, while region size did not benefit from the same linear model. This does not establish intelligence, agency, or self-modeling. It establishes only that one measured property of the observed trajectory was more predictable from short history than from a last-value baseline under the stated experiment.

The experiment remains external to the universe rules. No prediction is fed back into GenesisUniverse, GenesisConfig, phase, omega, or the coupling rule.

## Measurement rule

For regions A and B:

J(A,B) = |A intersection B| / |A union B|

A current region inherits a previous identity when J(A,B) >= overlap_threshold and that previous identity has not already been assigned in the current frame.

Lifecycle events are then derived from the overlap graph between consecutive observation frames.

## Non-interference rule

GENESIS-1.4 must not:

- write identities, lifecycle events, or memory records into GenesisUniverse
- modify phase, frequency, amplitude, coupling, or noise
- introduce endogenous memory
- introduce goals, meaning, language, agency, or self-models

The next experimental question is predictive value: whether the temporal trace contains information about a future region state beyond a suitable baseline.
