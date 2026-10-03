from __future__ import annotations

from genesis.core import GenesisConfig, GenesisUniverse
from genesis.local import LocalPatchPredictor
from genesis.memory import TemporalMemory
from genesis.observer import LocalStructureObserver, RegionTracker


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
    print("seed samples baseline_mae local_mae shuffled_mae improvement")
    for seed in (390001, 390002, 390003):
        result = LocalPatchPredictor().evaluate(collect(seed))
        print(
            seed,
            result.samples,
            f"{result.baseline_mae:.15g}",
            f"{result.local_mae:.15g}",
            f"{result.shuffled_mae:.15g}",
            f"{result.improvement:.15g}",
        )


if __name__ == "__main__":
    main()
