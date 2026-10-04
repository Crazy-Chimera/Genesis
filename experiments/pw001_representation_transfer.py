from __future__ import annotations

from genesis.core import GenesisConfig, GenesisUniverse
from genesis.memory import TemporalMemory
from genesis.observer import LocalStructureObserver, RegionTracker
from genesis.representation_transfer import RepresentationTransferPredictor


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


def main() -> None:
    records = {seed: collect(seed) for seed in (390001, 390002, 390003)}
    print("GENESIS-2.17 cross-seed representation transfer; ticks=2000")
    for source in records:
        for target in records:
            if source == target:
                continue
            for components in (2, 4, 8):
                for history in (2, 3, 5):
                    result = RepresentationTransferPredictor(
                        components=components, history_length=history
                    ).evaluate(records[source], records[target], source, target)
                    print(
                        source, target, components, history, result.samples,
                        f"{result.zero_mae:.15g}",
                        f"{result.transfer_mae:.15g}",
                        f"{result.shuffled_mae:.15g}",
                        f"{result.improvement:.15g}",
                        result.beats_zero, result.beats_shuffled,
                    )


if __name__ == "__main__":
    main()
