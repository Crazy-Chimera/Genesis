from __future__ import annotations

from genesis.core import GenesisConfig, GenesisUniverse
from genesis.memory import TemporalMemory
from genesis.observer import LocalStructureObserver, RegionTracker
from genesis.population_compressed_trajectory import PopulationCompressedTrajectoryPredictor


def collect(seed: int, ticks: int = 2_000):
    universe = GenesisUniverse(GenesisConfig(seed=seed, ticks=ticks))
    tracker = RegionTracker(LocalStructureObserver())
    memory = TemporalMemory()
    observations, events = tracker.observe_events(universe.phase)
    memory.record(universe.tick, observations, events)
    for _ in range(ticks):
        universe.step()
        observations, events = tracker.observe_events(universe.phase)
        memory.record(universe.tick, observations, events)
    return memory.all()


def main() -> None:
    print("GENESIS-2.19 population-state PCA trajectory screening")
    for seed in (390001, 390002, 390003):
        records = collect(seed)
        for components in (2, 4, 8):
            for history_length in (2, 3, 5):
                result = PopulationCompressedTrajectoryPredictor(
                    components=components,
                    history_length=history_length,
                    train_fraction=0.5,
                    ridge=1e-6,
                    require_consecutive=True,
                ).evaluate(records)
                print(
                    seed,
                    components,
                    history_length,
                    result.samples,
                    f"{result.zero_mae:.15g}",
                    f"{result.trajectory_mae:.15g}",
                    f"{result.shuffled_mae:.15g}",
                    f"{result.improvement:.15g}",
                    result.beats_zero,
                    result.beats_shuffled,
                )


if __name__ == "__main__":
    main()
