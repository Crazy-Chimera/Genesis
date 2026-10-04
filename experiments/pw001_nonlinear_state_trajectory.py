from __future__ import annotations

import argparse

from genesis.core import GenesisConfig, GenesisUniverse
from genesis.memory import TemporalMemory
from genesis.observer import LocalStructureObserver, RegionTracker
from genesis.nonlinear_state_trajectory import NonlinearStateTrajectoryPredictor


def collect(seed: int, ticks: int = 2_000):
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ticks", type=int, default=2_000)
    args = parser.parse_args()
    if args.ticks < 100:
        raise SystemExit("--ticks must be >= 100")

    print(f"GENESIS-2.14 nonlinear state-trajectory benchmark ticks={args.ticks}")
    for seed in (390001, 390002, 390003):
        records = collect(seed, args.ticks)
        for history_length in (2, 3, 5, 10):
            result = NonlinearStateTrajectoryPredictor(
                feature_name="combined",
                history_length=history_length,
                train_fraction=0.5,
                ridge=1e-4,
                random_features=256,
                random_seed=390001,
                require_consecutive=True,
            ).evaluate(records)
            print(
                seed,
                history_length,
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
