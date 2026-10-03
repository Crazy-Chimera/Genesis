# GENESIS-PW-001 — Baseline Reference Run

Date: 2026-10-03
Seed: 390001
Oscillators: 256
Topology: periodic 16×16, four-neighbour local coupling
Coupling: 0.01
Noise: 0.001
dt: 0.01
Ticks: 100000

## Reference observation

The baseline implementation was executed with the same numerical update rule as `genesis/core.py`.

Global coherence, measured every 10,000 ticks:

| Tick | Coherence |
|---:|---:|
| 10000 | 0.083558817 |
| 20000 | 0.031657158 |
| 30000 | 0.094255047 |
| 40000 | 0.078464166 |
| 50000 | 0.027447026 |
| 60000 | 0.059929413 |
| 70000 | 0.058070107 |
| 80000 | 0.059906600 |
| 90000 | 0.022553264 |
| 100000 | 0.095075481 |

## Interpretation

This single global coherence observable does not demonstrate the emergence of persistent entities. It only provides a reproducible baseline measurement.

The run remains compatible with a largely incoherent global state: coherence stays well below 1 and fluctuates over the run.

The next experiment therefore needs **local structure detection**, persistence tracking, and cluster identity tracking. Global coherence alone cannot distinguish a localized persistent structure from unrelated phase fluctuations.

## Verification status

This is a reference numerical execution of the repository's current update rule. GitHub Actions must still independently verify installation and tests on the repository runner.
