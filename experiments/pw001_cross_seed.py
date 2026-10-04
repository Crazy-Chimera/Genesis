from __future__ import annotations

from genesis.core import GenesisConfig, GenesisUniverse
from genesis.cross_seed import CrossSeedTrajectoryPredictor
from genesis.memory import TemporalMemory
from genesis.observer import LocalStructureObserver, RegionTracker


SEEDS = (390001, 390002, 390003)
HISTORIES = (2, 3, 5, 10)
TICKS = 2_000


def collect(seed: int):
    universe = GenesisUniverse(GenesisConfig(seed=seed, ticks=TICKS))
    observer = LocalStructureObserver()
    tracker = RegionTracker(observer)
    memory = TemporalMemory()

    observations, events = tracker.observe_events(universe.phase)
    memory.record(universe.tick, observations, events)

    for _ in range(TICKS):
        universe.step()
        observations, events = tracker.observe_events(universe.phase)
        memory.record(universe.tick, observations, events)

    return memory.all()


def main() -> None:
    records = {seed: collect(seed) for seed in SEEDS}
    print("GENESIS-2.17 cross-seed state-trajectory transfer screening")
    print(
        "train_seed test_seed history samples zero_mae transfer_mae "
        "shuffled_mae improvement beats_zero beats_shuffled"
    )

    for train_seed in SEEDS:
        for test_seed in SEEDS:
            if train_seed == test_seed:
                continue
            for history_length in HISTORIES:
                result = CrossSeedTrajectoryPredictor(
                    history_length=history_length,
                    train_fraction=0.5,
                    ridge=1e-6,
                    require_consecutive=True,
                ).evaluate(
                    records[train_seed],
                    records[test_seed],
                    train_seed=train_seed,
                    test_seed=test_seed,
                )
                print(
                    train_seed,
                    test_seed,
                    history_length,
                    result.samples,
                    f"{result.zero_mae:.15g}",
                    f"{result.transfer_mae:.15g}",
                    f"{result.shuffled_mae:.15g}",
                    f"{result.improvement:.15g}",
                    result.beats_zero,
                    result.beats_shuffled,
                )


if __name__ == "__main__":
    main()
