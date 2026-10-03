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

The observer now measures:

1. **Persistence** — number of observed frames for which the same region identity is maintained.
2. **Lifetime** — consecutive observation count for a tracked region.
3. **Boundary contrast** — difference between coherence inside a region and coherence immediately outside its boundary.
4. **Identity overlap** — Jaccard overlap between the current and previous cell sets.

Region identity is assigned by the observer using spatial overlap only. It is not part of the universe state.

The resulting RegionObservation is still an external measurement record, not an endogenous entity.

## Measurement rule

For regions A and B:

J(A,B) = |A intersection B| / |A union B|

A current region inherits the previous identity when J(A,B) >= overlap_threshold and that previous identity has not already been assigned in the current frame.

New regions receive a new observer-local identity.

## Non-interference rule

GENESIS-1.2 must not:

- write identities into GenesisUniverse
- modify phase, frequency, amplitude, coupling, or noise
- introduce memory into the universe
- introduce goals, meaning, language, agency, or self-models

The next experimental question is whether measured persistence and identity continuity provide a useful empirical basis for a later memory layer.
