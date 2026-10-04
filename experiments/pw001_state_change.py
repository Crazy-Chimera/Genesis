from __future__ import annotations

from genesis.core import GenesisConfig, GenesisUniverse
from genesis.memory import TemporalMemory
from genesis.observer import LocalStructureObserver, RegionTracker
from genesis.state_delta_trajectory import StateDeltaTrajectoryPredictor
from genesis.state_velocity import StateVelocityPredictor


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
    print("GENESIS-2.13 state-change benchmark")
    for seed in (390001, 390002, 390003):
        records = collect(seed)
        print(f"seed={seed} records={len(records)}")
        for history_length in (2, 3, 5, 10):
            velocity = StateVelocityPredictor(
                history_length=history_length, require_consecutive=True
            ).evaluate(records)
            delta = StateDeltaTrajectoryPredictor(
                feature_name="combined",
                history_length=history_length,
                require_consecutive=True,
            ).evaluate(records)
            print(
                seed, history_length,
                "velocity",
                velocity.samples,
                f"{velocity.zero_mae:.15g}",
                f"{velocity.velocity_mae:.15g}",
                f"{velocity.shuffled_mae:.15g}",
                f"{velocity.improvement:.15g}",
                velocity.beats_zero,
                velocity.beats_shuffled,
                "delta",
                delta.samples,
                f"{delta.zero_mae:.15g}",
                f"{delta.delta_mae:.15g}",
                f"{delta.shuffled_mae:.15g}",
                f"{delta.improvement:.15g}",
                delta.beats_zero,
                delta.beats_shuffled,
            )


if __name__ == "__main__":
    main()
