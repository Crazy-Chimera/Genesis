from __future__ import annotations

from genesis.core import GenesisConfig, GenesisUniverse
from genesis.memory import TemporalMemory
from genesis.observer import LocalStructureObserver, RegionTracker
from genesis.state_trajectory import StateTrajectoryPredictor
from genesis.state_innovation import STATE_FEATURES


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
    print("GENESIS-2.13 single-representation state-trajectory sweep")
    for seed in (390001, 390002, 390003):
        records = collect(seed)
        for spec in STATE_FEATURES:
            for history_length in (2, 3, 5, 10):
                result = StateTrajectoryPredictor(
                    feature_name=spec.name,
                    history_length=history_length,
                    train_fraction=0.5,
                    ridge=1e-6,
                    require_consecutive=True,
                ).evaluate(records)
                print(
                    seed,
                    spec.name,
                    spec.width,
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
