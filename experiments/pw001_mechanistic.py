from __future__ import annotations

from genesis.core import GenesisConfig, GenesisUniverse
from genesis.mechanistic import MechanisticOneStepPredictor


def main() -> None:
    print("GENESIS-2.36 mechanistic one-step rule benchmark")
    print("seed samples zero_mae mechanistic_mae improvement beats_zero")
    for seed in (390001, 390002, 390003, 390004, 390005, 390006):
        universe = GenesisUniverse(GenesisConfig(seed=seed, ticks=2_000))
        result = MechanisticOneStepPredictor().evaluate(universe)
        print(
            seed,
            result.samples,
            f"{result.zero_mae:.15g}",
            f"{result.mechanistic_mae:.15g}",
            f"{result.improvement:.15g}",
            result.beats_zero,
        )


if __name__ == "__main__":
    main()
