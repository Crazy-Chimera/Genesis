from __future__ import annotations

import numpy as np

from genesis.core import GenesisConfig, GenesisUniverse
from genesis.rule_native import RuleNativePredictor, rule_native_features

SEEDS = (390001, 390002, 390003, 390004, 390005, 390006)
TICKS = 500


def collect(seed: int):
    u = GenesisUniverse(GenesisConfig(seed=seed, ticks=TICKS))
    rows = []
    previous = None
    for _ in range(TICKS + 1):
        features = rule_native_features(u.phase, u.omega)
        coherence = float(abs(np.mean(np.exp(1j * u.phase))))
        if previous is not None:
            rows.append((features, coherence - previous))
        previous = coherence
        u.step()
    return rows


def main() -> None:
    records = {seed: collect(seed) for seed in SEEDS}
    results = []
    print(f"GENESIS-2.24 rule-native cross-seed screening; seeds={SEEDS}; ticks={TICKS}")
    for target in SEEDS:
        train = [row for seed in SEEDS if seed != target for row in records[seed][:TICKS // 2]]
        test = records[target][TICKS // 2:]
        result = RuleNativePredictor().fit_predict(train, test)
        results.append(result)
        print(
            target, result.samples,
            f"{result.zero_mae:.15g}",
            f"{result.rule_mae:.15g}",
            f"{result.shuffled_mae:.15g}",
            f"{result.improvement:.15g}",
            result.beats_zero,
            result.beats_shuffled,
        )
    print("SUMMARY")
    print(f"cases={len(results)}")
    print(f"beats_zero={sum(r.beats_zero for r in results)}")
    print(f"beats_shuffled={sum(r.beats_shuffled for r in results)}")
    print(f"mean_zero_mae={sum(r.zero_mae for r in results)/len(results):.15g}")
    print(f"mean_rule_mae={sum(r.rule_mae for r in results)/len(results):.15g}")
    print(f"mean_shuffled_mae={sum(r.shuffled_mae for r in results)/len(results):.15g}")
    print(f"mean_improvement={sum(r.improvement for r in results)/len(results):.15g}")


if __name__ == "__main__":
    main()
