from genesis.core import GenesisConfig, GenesisUniverse
from genesis.memory import TemporalMemory
from genesis.observer import LocalStructureObserver, RegionTracker
from genesis.direct_state_transfer import DirectStateTransferPredictor


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
    results = []
    print("GENESIS-2.21 direct cross-seed 193D state transfer; ticks=2000")
    for source in records:
        for target in records:
            if source == target:
                continue
            for history in (2, 3, 5):
                result = DirectStateTransferPredictor(
                    history_length=history
                ).evaluate(records[source], records[target], source, target)
                results.append(result)
                print(
                    source, target, history, result.samples,
                    f"{result.zero_mae:.15g}",
                    f"{result.transfer_mae:.15g}",
                    f"{result.shuffled_mae:.15g}",
                    f"{result.improvement:.15g}",
                    result.beats_zero, result.beats_shuffled,
                )

    zero_beats = sum(r.beats_zero for r in results)
    shuffled_beats = sum(r.beats_shuffled for r in results)
    mean_zero = sum(r.zero_mae for r in results) / len(results)
    mean_transfer = sum(r.transfer_mae for r in results) / len(results)
    mean_shuffled = sum(r.shuffled_mae for r in results) / len(results)
    print("SUMMARY")
    print(f"cases={len(results)}")
    print(f"beats_zero={zero_beats}")
    print(f"beats_shuffled={shuffled_beats}")
    print(f"mean_zero_mae={mean_zero:.15g}")
    print(f"mean_transfer_mae={mean_transfer:.15g}")
    print(f"mean_shuffled_mae={mean_shuffled:.15g}")
    print(f"mean_improvement={mean_zero - mean_transfer:.15g}")
    print(
        "decision=" + (
            "positive"
            if zero_beats == len(results) and shuffled_beats == len(results)
            else "negative"
        )
    )


if __name__ == "__main__":
    main()
