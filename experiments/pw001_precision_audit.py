from __future__ import annotations

from genesis.core import GenesisConfig, GenesisUniverse
from genesis.precision_audit import evaluate_precision_audit

SEEDS = tuple(range(390067, 390073))
HORIZONS = (1, 2, 5, 10)
TICKS = 2_000


def main() -> None:
    print("GENESIS-2.45 numerical precision audit")
    print(
        "seed horizon samples mean_coherence_gap max_coherence_gap "
        "mean_phase_gap max_phase_gap"
    )
    for seed in SEEDS:
        for horizon in HORIZONS:
            result = evaluate_precision_audit(
                GenesisUniverse(GenesisConfig(seed=seed, ticks=TICKS)),
                horizon,
            )
            print(
                seed,
                horizon,
                result.samples,
                f"{result.mean_coherence_gap:.15g}",
                f"{result.max_coherence_gap:.15g}",
                f"{result.mean_phase_gap:.15g}",
                f"{result.max_phase_gap:.15g}",
            )


if __name__ == "__main__":
    main()
