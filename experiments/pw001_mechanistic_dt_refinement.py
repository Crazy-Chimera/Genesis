from __future__ import annotations

from genesis.core import GenesisConfig, GenesisUniverse
from genesis.mechanistic import MechanisticOneStepPredictor

SEEDS = (390067, 390068, 390069, 390070, 390071, 390072)
DTS = (0.01, 0.005, 0.0025, 0.00125)
TICKS = 2_000


def main() -> None:
    print("GENESIS-2.46 mechanistic dt refinement")
    print("seed dt samples zero_mae mechanistic_mae improvement ratio")
    for seed in SEEDS:
        for dt in DTS:
            result = MechanisticOneStepPredictor().evaluate(
                GenesisUniverse(
                    GenesisConfig(
                        seed=seed,
                        dt=dt,
                        ticks=TICKS,
                    )
                )
            )
            ratio = (
                result.mechanistic_mae / result.zero_mae
                if result.zero_mae
                else 0.0
            )
            print(
                seed,
                dt,
                result.samples,
                f"{result.zero_mae:.15g}",
                f"{result.mechanistic_mae:.15g}",
                f"{result.improvement:.15g}",
                f"{ratio:.15g}",
            )


if __name__ == "__main__":
    main()
