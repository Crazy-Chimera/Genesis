# GENESIS

**GENESIS** is the experimental substrate for Agent Ω.

The first goal is deliberately smaller than AGI: test whether persistent relational structure can emerge from a minimal set of local rules without explicitly encoding entities, goals, language, memory, or intelligence.

## GENESIS-PW-001

Baseline primordial-wave experiment:

- N = 256 oscillators arranged on a periodic 16×16 lattice
- random initial phase
- natural frequency ~ Normal(1.0, 0.05)
- initial amplitude = 1.0
- fixed local coupling K = 0.01
- deterministic noise
- seed = 390001
- 100,000 ticks
- no entity, goal, language, memory, or self-model is part of the universe rules

The observer measures coherence and other properties externally. A detected pattern is not automatically an entity.

## Development process

GENESIS follows the project's evolutionary process:

**context → module → test → integration → deployment → verification → iteration**

The process is primary; the format is secondary. Every change must be reproducible and verified.

## Run

```bash
python -m genesis
```

For a short run:

```bash
python -m genesis --ticks 1000
```

Tests:

```bash
python -m pytest
```
