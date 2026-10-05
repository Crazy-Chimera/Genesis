from __future__ import annotations

import numpy as np

from genesis.core import GenesisConfig, GenesisUniverse
from genesis.rule_transition import RuleTransitionPredictor, rule_transition_features

SEEDS = tuple(range(390013, 390025))
TICKS = 600
TRAIN_END = 300
GAP_END = 450


def collect(seed: int):
    universe = GenesisUniverse(GenesisConfig(seed=seed, ticks=TICKS))
    rows = []
    previous_phase = universe.phase.copy()
    previous_coherence = float(abs(np.mean(np.exp(1j * previous_phase))))

    for _ in range(TICKS):
        universe.step()
        phase = universe.phase
        coherence = float(abs(np.mean(np.exp(1j * phase))))
        features = rule_transition_features(
            previous_phase, phase, universe.omega, universe.config.coupling
        )
        rows.append((features, coherence - previous_coherence))
        previous_phase = phase.copy()
        previous_coherence = coherence
    return rows


def main() -> None:
    records = {seed: collect(seed) for seed in SEEDS}
    results = []

    print(
        "GENESIS-2.31 extended unseen-seed replication; "
        f"seeds={SEEDS}; ticks={TICKS}; train=0:{TRAIN_END}; "
        f"gap={TRAIN_END}:{GAP_END}; test={GAP_END}:{TICKS}"
    )

    for target in SEEDS:
        train = [
            row
            for seed in SEEDS
            if seed != target
            for row in records[seed][:TRAIN_END]
        ]
        test = records[target][GAP_END:TICKS]
        result = RuleTransitionPredictor().fit_predict(train, test)
        results.append(result)
        print(
            target,
            result.samples,
            f"{result.zero_mae:.15g}",
            f"{result.transition_mae:.15g}",
            f"{result.shuffled_mae:.15g}",
            f"{result.improvement:.15g}",
            result.beats_zero,
            result.beats_shuffled,
        )

    n = len(results)
    print("SUMMARY")
    print(f"cases={n}")
    print(f"beats_zero={sum(r.beats_zero for r in results)}")
    print(f"beats_shuffled={sum(r.beats_shuffled for r in results)}")
    print(f"mean_zero_mae={sum(r.zero_mae for r in results) / n:.15g}")
    print(f"mean_transition_mae={sum(r.transition_mae for r in results) / n:.15g}")
    print(f"mean_shuffled_mae={sum(r.shuffled_mae for r in results) / n:.15g}")
    print(f"mean_improvement={sum(r.improvement for r in results) / n:.15g}")


if __name__ == "__main__":
    main()
