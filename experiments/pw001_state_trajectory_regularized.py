from __future__ import annotations

from genesis.core import GenesisConfig, GenesisUniverse
from genesis.memory import TemporalMemory
from genesis.observer import LocalStructureObserver, RegionTracker
from genesis.state_trajectory_regularized import RegularizedStateTrajectoryPredictor


def collect(seed: int, ticks: int = 10_000):
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
    print("GENESIS-2.13 regularized state-trajectory benchmark")
    for seed in (390001, 390002, 390003):
        records = collect(seed)
        for history_length in (2, 3, 5, 10):
            result = RegularizedStateTrajectoryPredictor(
                feature_name="combined",
                history_length=history_length,
                train_fraction=0.5,
                validation_fraction=0.25,
                ridges=(1e-6, 1e-4, 1e-2, 1.0, 100.0, 10_000.0),
            ).evaluate(records)
            print(
                seed, history_length, result.samples,
                f"{result.zero_mae:.15g}",
                f"{result.trajectory_mae:.15g}",
                f"{result.shuffled_mae:.15g}",
                f"{result.improvement:.15g}",
                result.ridge,
                result.beats_zero,
                result.beats_shuffled,
            )


if __name__ == "__main__":
    main()
