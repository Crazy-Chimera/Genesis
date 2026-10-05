from __future__ import annotations

from genesis.core import GenesisConfig, GenesisUniverse
from genesis.mechanistic_decomposition import MechanisticDecompositionEvaluator


def main() -> None:
    print("GENESIS-2.37 mechanistic coupling decomposition")
    print(
        "seed samples zero_mae frequency_only_mae full_rule_mae "
        "full_vs_frequency_improvement full_beats_frequency"
    )
    for seed in (390001, 390002, 390003, 390004, 390005, 390006):
        universe = GenesisUniverse(GenesisConfig(seed=seed, ticks=2_000))
        result = MechanisticDecompositionEvaluator().evaluate(universe)
        print(
            seed,
            result.samples,
            f"{result.zero_mae:.15g}",
            f"{result.frequency_only_mae:.15g}",
            f"{result.full_rule_mae:.15g}",
            f"{result.full_vs_frequency_improvement:.15g}",
            result.full_beats_frequency_only,
        )


if __name__ == "__main__":
    main()
