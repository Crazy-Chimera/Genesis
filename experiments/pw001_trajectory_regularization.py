from __future__ import annotations

from genesis.core import GenesisConfig, GenesisUniverse
from genesis.memory import TemporalMemory
from genesis.observer import LocalStructureObserver, RegionTracker
from genesis.state_trajectory import StateTrajectoryPredictor


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
    print("GENESIS-2.13 trajectory regularization diagnostic")
    for seed in (390001, 390002, 390003):
        records = collect(seed)
        print(f"seed={seed}")
        print("history ridge samples zero_mae trajectory_mae improvement beats_zero")
        for history_length in (2, 3, 5, 10):
            for ridge in (1e-6, 1e-4, 1e-2, 1.0, 100.0):
                result = StateTrajectoryPredictor(
                    feature_name="combined",
                    history_length=history_length,
                    train_fraction=0.5,
                    ridge=ridge,
                    require_consecutive=True,
                ).evaluate(records)
                print(
                    history_length,
                    f"{ridge:.0e}",
                    result.samples,
                    f"{result.zero_mae:.15g}",
                    f"{result.trajectory_mae:.15g}",
                    f"{result.improvement:.15g}",
                    result.beats_zero,
                )


if __name__ == "__main__":
    main()
