from __future__ import annotations

from genesis.core import GenesisConfig, GenesisUniverse
from genesis.memory import TemporalMemory
from genesis.observer import LocalStructureObserver, RegionTracker
from genesis.state_trajectory_pca import StateTrajectoryPCAPredictor


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
    print("GENESIS-2.13 PCA-compressed state-trajectory benchmark")
    for seed in (390001, 390002, 390003):
        records = collect(seed)
        print(f"seed={seed} records={len(records)}")
        for history_length in (2, 3, 5, 10):
            for components in (2, 4, 8, 16):
                result = StateTrajectoryPCAPredictor(
                    history_length=history_length,
                    components=components,
                    train_fraction=0.5,
                    ridge=1e-6,
                    require_consecutive=True,
                ).evaluate(records)
                print(
                    seed, history_length, components, result.samples,
                    f"{result.zero_mae:.15g}",
                    f"{result.pca_mae:.15g}",
                    f"{result.shuffled_mae:.15g}",
                    f"{result.improvement:.15g}",
                    result.beats_zero, result.beats_shuffled,
                )


if __name__ == "__main__":
    main()
