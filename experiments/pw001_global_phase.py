from __future__ import annotations

from genesis.core import GenesisConfig, GenesisUniverse
from genesis.global_phase import GlobalPhasePredictor


def collect(seed: int, ticks: int = 10_000):
    universe = GenesisUniverse(GenesisConfig(seed=seed, ticks=ticks))
    records = [(0, universe.phase.copy(), 0.0)]

    def coherence(phase):
        return float(abs(__import__("numpy").mean(__import__("numpy").exp(1j * phase))))

    records[0] = (0, universe.phase.copy(), coherence(universe.phase))

    for _ in range(ticks):
        universe.step()
        records.append((universe.tick, universe.phase.copy(), coherence(universe.phase)))

    return records


def main() -> None:
    print("GENESIS-2.35 global-phase benchmark")
    for seed in (390001, 390002, 390003):
        result = GlobalPhasePredictor(
            train_fraction=0.5,
            ridge=1e-3,
            require_consecutive=True,
        ).evaluate(collect(seed))
        print(
            seed,
            result.samples,
            f"{result.zero_mae:.15g}",
            f"{result.phase_mae:.15g}",
            f"{result.shuffled_mae:.15g}",
            f"{result.improvement:.15g}",
            result.beats_zero,
            result.beats_shuffled,
        )


if __name__ == "__main__":
    main()
