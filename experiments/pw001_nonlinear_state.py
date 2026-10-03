from __future__ import annotations

from genesis.core import GenesisConfig, GenesisUniverse
from genesis.memory import TemporalMemory
from genesis.nonlinear_state import NonlinearStatePredictor
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
    print("GENESIS-2.13 nonlinear state-model-class control")
    for seed in (390001, 390002, 390003):
        records = collect(seed)
        for feature_count in (32, 64, 128):
            result = NonlinearStatePredictor(
                feature_count=feature_count,
                ridge=1e-3,
                seed=390001,
                train_fraction=0.5,
                require_consecutive=True,
            ).evaluate(records)
            print(
                seed,
                feature_count,
                result.samples,
                f"{result.zero_mae:.15g}",
                f"{result.nonlinear_mae:.15g}",
                f"{result.shuffled_mae:.15g}",
                f"{result.improvement:.15g}",
                result.beats_zero,
                result.beats_shuffled,
            )


if __name__ == "__main__":
    main()
