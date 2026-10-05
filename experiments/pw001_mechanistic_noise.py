from __future__ import annotations

from genesis.core import GenesisConfig, GenesisUniverse
from genesis.mechanistic_noise import evaluate_noise_audit

SEEDS = tuple(range(390061, 390067))
HORIZONS = (1, 2, 5, 10)
TICKS = 2_000


def main() -> None:
    print("GENESIS-2.44 mechanistic noise attribution audit")
    print("seed horizon samples deterministic_mae noise_effect_mae")
    for seed in SEEDS:
        for horizon in HORIZONS:
            result = evaluate_noise_audit(
                GenesisUniverse(GenesisConfig(seed=seed, ticks=TICKS)),
                horizon,
            )
            print(
                seed,
                horizon,
                result.samples,
                f"{result.deterministic_mae:.15g}",
                f"{result.noise_effect_mae:.15g}",
            )


if __name__ == "__main__":
    main()
