from __future__ import annotations

from genesis.core import GenesisConfig, GenesisUniverse
from genesis.evaluation import PredictiveEvaluator
from genesis.memory import TemporalMemory
from genesis.observer import LocalStructureObserver, RegionTracker


def collect(ticks: int = 10_000):
    config = GenesisConfig(ticks=ticks)
    universe = GenesisUniverse(config)
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
    records = collect()
    print(f"records={len(records)}")
    print(f"identities={len({r.identity for r in records})}")

    for history_length in (1, 2, 3, 5, 10):
        result = PredictiveEvaluator(
            history_length=history_length,
            train_fraction=0.5,
            require_consecutive=True,
        ).evaluate(records)
        print(
            history_length,
            result.samples,
            f"{result.baseline_mae:.15g}",
            f"{result.history_mae:.15g}",
            f"{result.shuffled_mae:.15g}",
            f"{result.improvement:.15g}",
        )


if __name__ == "__main__":
    main()
