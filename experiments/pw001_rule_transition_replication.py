from __future__ import annotations

import numpy as np

from genesis.core import GenesisConfig, GenesisUniverse
from genesis.rule_transition import RuleTransitionPredictor, rule_transition_features

SOURCE_SEEDS = tuple(range(390013, 390025))
TARGET_SEEDS = tuple(range(390025, 390037))
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
    source = {seed: collect(seed) for seed in SOURCE_SEEDS}
    target = {seed: collect(seed) for seed in TARGET_SEEDS}
    train = [
        row
        for seed in SOURCE_SEEDS
        for row in source[seed][:TRAIN_END]
    ]

    results = []
    print(
        "GENESIS-2.32 independent unseen-seed replication; "
        f"source={SOURCE_SEEDS}; target={TARGET_SEEDS}; "
        f"train=0:{TRAIN_END}; gap={TRAIN_END}:{GAP_END}; test={GAP_END}:{TICKS}"
    )

    for seed in TARGET_SEEDS:
        result = RuleTransitionPredictor().fit_predict(
            train, target[seed][GAP_END:TICKS]
        )
        results.append(result)
        print(
            seed, result.samples,
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
