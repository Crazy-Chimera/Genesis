from __future__ import annotations

from genesis.core import GenesisConfig, GenesisUniverse
from genesis.memory import TemporalMemory
from genesis.observer import LocalStructureObserver, RegionTracker
from genesis.state_trajectory import StateTrajectoryPredictor


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


def evaluate(records, history_length: int, differences: bool):
    return StateTrajectoryPredictor(
        feature_name="combined",
        history_length=history_length,
        train_fraction=0.5,
        ridge=1e-6,
        require_consecutive=True,
        differences=differences,
    ).evaluate(records)


def main() -> None:
    print("GENESIS-2.13 incremental state-delta benchmark")
    for seed in (390001, 390002, 390003):
        records = collect(seed)
        print(
            f"seed={seed} records={len(records)} "
            f"identities={len({r.identity for r in records})}"
        )
        print(
            "seed history_length representation samples zero_mae "
            "trajectory_mae shuffled_mae improvement beats_zero beats_shuffled"
        )
        for history_length in (2, 3, 5, 10):
            for differences in (False, True):
                result = evaluate(records, history_length, differences)
                representation = "delta" if differences else "absolute"
                print(
                    seed,
                    history_length,
                    representation,
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
