from __future__ import annotations

import numpy as np

from genesis.core import GenesisConfig, GenesisUniverse
from genesis.memory import MemoryRecord, TemporalMemory
from genesis.observer import LocalStructureObserver, RegionTracker


def collect(seed: int, ticks: int = 600):
    universe = GenesisUniverse(GenesisConfig(seed=seed, ticks=ticks))
    observer = LocalStructureObserver()
    tracker = RegionTracker(observer)
    memory = TemporalMemory()
    frequency: dict[tuple[int, int], tuple[float, ...]] = {}

    def record_frame() -> None:
        observations, events = tracker.observe_events(universe.phase)
        added = memory.record(universe.tick, observations, events)
        for record in added:
            values = np.asarray([universe.omega[r, c] for r, c in record.cells], dtype=float)
            if values.size == 0:
                feature = (0.0, 0.0, 0.0)
            else:
                feature = (
                    float(values.mean()),
                    float(values.std()),
                    float(np.mean(np.abs(values - universe.omega.mean()))),
                )
            frequency[(record.tick, record.identity)] = feature

    record_frame()
    for _ in range(ticks):
        universe.step()
        record_frame()
    return memory.all(), frequency


def pairs(records: list[MemoryRecord] | tuple[MemoryRecord, ...]):
    by_id: dict[int, list[MemoryRecord]] = {}
    for record in records:
        by_id.setdefault(record.identity, []).append(record)
    for items in by_id.values():
        items.sort(key=lambda item: item.tick)
    for items in by_id.values():
        for current, target in zip(items, items[1:]):
            if target.tick == current.tick + 1:
                yield current, target


def evaluate(train_records, train_frequency, test_records, test_frequency, ridge=1e-6):
    train_x, train_y = [], []
    for current, target in pairs(train_records):
        train_x.append(train_frequency[(current.tick, current.identity)])
        train_y.append(target.coherence - current.coherence)

    test_x, test_y = [], []
    for current, target in pairs(test_records):
        test_x.append(test_frequency[(current.tick, current.identity)])
        test_y.append(target.coherence - current.coherence)

    train_x = np.asarray(train_x, dtype=float)
    train_y = np.asarray(train_y, dtype=float)
    test_x = np.asarray(test_x, dtype=float)
    test_y = np.asarray(test_y, dtype=float)

    mean = train_x.mean(axis=0)
    scale = train_x.std(axis=0)
    scale[scale == 0.0] = 1.0
    X = np.column_stack((np.ones(len(train_x)), (train_x - mean) / scale))
    V = np.column_stack((np.ones(len(test_x)), (test_x - mean) / scale))
    regularizer = np.eye(X.shape[1])
    regularizer[0, 0] = 0.0
    coef = np.linalg.solve(
        X.T @ X + ridge * regularizer,
        X.T @ train_y,
    )
    prediction = V @ coef

    rng = np.random.default_rng(390001)
    permutation_mae = []
    for _ in range(25):
        shuffled = test_x.copy()
        rng.shuffle(shuffled)
        shuffled_prediction = np.column_stack(
            (np.ones(len(shuffled)), (shuffled - mean) / scale)
        ) @ coef
        permutation_mae.append(float(np.mean(np.abs(test_y - shuffled_prediction))))

    zero_mae = float(np.mean(np.abs(test_y)))
    model_mae = float(np.mean(np.abs(test_y - prediction)))
    return (
        len(test_y),
        zero_mae,
        model_mae,
        float(np.mean(permutation_mae)),
        zero_mae - model_mae,
    )


def main() -> None:
    print("GENESIS-2.34 local frequency-detuning transfer")
    source = tuple(range(390013, 390025))
    target = tuple(range(390025, 390037))
    source_data = [collect(seed) for seed in source]
    target_data = [collect(seed) for seed in target]

    results = []
    train_records = tuple(
        record for records, _ in source_data for record in records if record.tick < 300
    )
    train_frequency = {
        key: value
        for _, frequency in source_data
        for key, value in frequency.items()
        if key[0] < 300
    }

    for target_seed, (records, frequency) in zip(target, target_data):
        test_records = tuple(record for record in records if 450 <= record.tick < 600)
        test_frequency = {
            key: value
            for key, value in frequency.items()
            if 450 <= key[0] < 600
        }
        result = evaluate(
            train_records,
            train_frequency,
            test_records,
            test_frequency,
        )
        results.append(result)
        print(target_seed, *result)

    values = np.asarray(results, dtype=float)
    print(
        "aggregate",
        "targets=", len(results),
        "beats_zero=", int(np.sum(values[:, 2] < values[:, 1])),
        "beats_permutation=", int(np.sum(values[:, 2] < values[:, 3])),
        "mean_zero=", float(values[:, 1].mean()),
        "mean_model=", float(values[:, 2].mean()),
        "mean_permutation=", float(values[:, 3].mean()),
        "mean_improvement=", float(values[:, 4].mean()),
    )


if __name__ == "__main__":
    main()
