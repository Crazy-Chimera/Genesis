from __future__ import annotations

from genesis.core import GenesisConfig, GenesisUniverse
from genesis.mechanistic_horizon import evaluate_horizon

SEEDS = tuple(range(390055, 390061))
HORIZONS = (1, 2, 5, 10)
TICKS = 2_000


def main() -> None:
    print("GENESIS-2.43 mechanistic horizon validation")
    print("seed horizon samples zero_mae mechanistic_mae improvement beats_zero")
    for seed in SEEDS:
        for horizon in HORIZONS:
            result = evaluate_horizon(
                GenesisUniverse(GenesisConfig(seed=seed, ticks=TICKS)),
                horizon,
            )
            print(
                seed,
                horizon,
                result.samples,
                f"{result.zero_mae:.15g}",
                f"{result.mechanistic_mae:.15g}",
                f"{result.improvement:.15g}",
                result.beats_zero,
            )


if __name__ == "__main__":
    main()
