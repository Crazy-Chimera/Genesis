from genesis.core import GenesisConfig, GenesisUniverse
from genesis.memory import TemporalMemory
from genesis.observer import LocalStructureObserver, RegionTracker
from genesis.state_direction import StateDirectionPredictor


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


def main():
    print("GENESIS-2.13 state-direction benchmark")
    for seed in (390001, 390002, 390003):
        records = collect(seed)
        result = StateDirectionPredictor(
            feature_name="combined",
            train_fraction=0.5,
            ridge=1e-6,
            require_consecutive=True,
        ).evaluate(records)
        print(
            seed,
            result.samples,
            f"{result.majority_accuracy:.15g}",
            f"{result.direction_accuracy:.15g}",
            f"{result.shuffled_accuracy:.15g}",
            f"{result.improvement:.15g}",
            result.beats_majority,
            result.beats_shuffled,
        )


if __name__ == "__main__":
    main()
