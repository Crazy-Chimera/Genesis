from __future__ import annotations

from genesis.core import GenesisConfig, GenesisUniverse
from genesis.memory import TemporalMemory
from genesis.observer import LocalStructureObserver, RegionTracker
from genesis.state_transition import StateTransitionPredictor


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
    print("GENESIS-2.13 state-transition benchmark")
    print(
        "seed samples zero_mae transition_mae shuffled_mae "
        "improvement beats_zero beats_shuffled"
    )
    for seed in (390001, 390002, 390003):
        result = StateTransitionPredictor(
            train_fraction=0.5,
            ridge=1e-6,
            require_consecutive=True,
        ).evaluate(collect(seed))
        print(
            seed,
            result.samples,
            f"{result.zero_mae:.15g}",
            f"{result.transition_mae:.15g}",
            f"{result.shuffled_mae:.15g}",
            f"{result.improvement:.15g}",
            result.beats_zero,
            result.beats_shuffled,
        )


if __name__ == "__main__":
    main()
