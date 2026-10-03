from __future__ import annotations

from genesis.core import GenesisConfig, GenesisUniverse
from genesis.memory import TemporalMemory
from genesis.observer import LocalStructureObserver, RegionTracker
from genesis.structural import StructuralPredictor


def collect(seed: int, ticks: int = 10_000):
    universe = GenesisUniverse(GenesisConfig(seed=seed, ticks=ticks))
    observer = LocalStructureObserver()
    tracker = RegionTracker(observer)
    memory = TemporalMemory()

    observations, events = tracker.observe_events(universe.phase)
    memory.record(universe.tick, observations, events)

    for _ in range(ticks):
        universe.step()
        observations, events = tracker.observe_events(universe.phase)
        memory.record(universe.tick, observations, events)

    return memory.all()


def main() -> None:
    print(
        "seed samples baseline_mae structural_mae "
        "shuffled_mae improvement"
    )
    for seed in (390001, 390002, 390003):
        records = collect(seed)
        result = StructuralPredictor(
            train_fraction=0.5,
            require_consecutive=True,
        ).evaluate(records)
        print(
            seed,
            result.samples,
            f"{result.baseline_mae:.15g}",
            f"{result.structural_mae:.15g}",
            f"{result.shuffled_mae:.15g}",
            f"{result.improvement:.15g}",
        )


if __name__ == "__main__":
    main()
