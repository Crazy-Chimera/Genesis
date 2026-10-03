from __future__ import annotations

from genesis.core import GenesisConfig, GenesisUniverse
from genesis.evaluation import PredictiveEvaluator
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
    for seed in (390001, 390002, 390003):
        records = collect(seed)
        print(f"seed={seed} records={len(records)} identities={len({r.identity for r in records})}")
        for history_length in (2, 3, 5, 10):
            result = PredictiveEvaluator(
                history_length=history_length,
                train_fraction=0.5,
                require_consecutive=True,
            ).evaluate(records)
            print(
                seed,
                history_length,
                result.samples,
                f"{result.baseline_mae:.15g}",
                f"{result.history_mae:.15g}",
                f"{result.mean_mae:.15g}",
                f"{result.shuffled_mae:.15g}",
                f"{result.improvement:.15g}",
            )


if __name__ == "__main__":
    main()
