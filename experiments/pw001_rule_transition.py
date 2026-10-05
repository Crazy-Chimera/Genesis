from __future__ import annotations

import numpy as np

from genesis.core import GenesisConfig, GenesisUniverse
from genesis.rule_transition import RuleTransitionPredictor, rule_transition_features

SEEDS = (390001, 390002, 390003, 390004, 390005, 390006)
TICKS = 500


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
        "GENESIS-2.28 rule-transition cross-seed screening; "
        f"seeds={SEEDS}; ticks={TICKS}"
    )

    for target in SEEDS:
        train = [
            row
            for seed in SEEDS
            if seed != target
            for row in records[seed][: TICKS // 2]
        ]
        test = records[target][TICKS // 2 :]
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

    print("SUMMARY")
    print(f"cases={len(results)}")
    print(f"beats_zero={sum(r.beats_zero for r in results)}")
    print(f"beats_shuffled={sum(r.beats_shuffled for r in results)}")
    print(f"mean_zero_mae={sum(r.zero_mae for r in results) / len(results):.15g}")
    print(
        "mean_transition_mae="
        f"{sum(r.transition_mae for r in results) / len(results):.15g}"
    )
    print(
        "mean_shuffled_mae="
        f"{sum(r.shuffled_mae for r in results) / len(results):.15g}"
    )
    print(
        "mean_improvement="
        f"{sum(r.improvement for r in results) / len(results):.15g}"
    )


if __name__ == "__main__":
    main()
