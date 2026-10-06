from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from genesis.core import GenesisConfig, GenesisUniverse
from genesis.memory import TemporalMemory
from genesis.observer import LocalStructureObserver, RegionTracker
from genesis.state_innovation import STATE_FEATURES_WITH_COMBINED


@dataclass(frozen=True)
class Result:
    seed: int
    history: int
    ridge: float
    samples: int
    zero_mae: float
    state_mae: float
    shuffled_mae: float

    @property
    def improvement(self) -> float:
        return self.zero_mae - self.state_mae


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


def feature(record):
    spec = next(s for s in STATE_FEATURES_WITH_COMBINED if s.name == "combined")
    return np.asarray(spec.feature(record), dtype=float)


def evaluate(records, history, ridge):
    groups = {}
    for item in records:
        groups.setdefault(item.identity, []).append(item)

    all_items = sorted(records, key=lambda x: x.tick)
    lo, hi = all_items[0].tick, all_items[-1].tick
    split = lo + max(1, int((hi - lo) * 0.5))
    train_x, train_y, test_x, test_y = [], [], [], []

    for items in groups.values():
        items.sort(key=lambda x: x.tick)
        for i in range(history, len(items)):
            window = items[i-history:i]
            target = items[i]
            ticks = [x.tick for x in window] + [target.tick]
            if any(ticks[j+1] != ticks[j] + 1 for j in range(len(ticks)-1)):
                continue

            vectors = np.asarray([feature(x) for x in window])
            # Temporal compression: last state + first differences + mean/std
            diffs = np.diff(vectors, axis=0).reshape(-1)
            last = vectors[-1]
            mean = vectors.mean(axis=0)
            std = vectors.std(axis=0)
            row = np.concatenate((last, diffs, mean, std))
            delta = target.coherence - window[-1].coherence

            if target.tick < split:
                train_x.append(row); train_y.append(delta)
            else:
                test_x.append(row); test_y.append(delta)

    if not train_x or not test_x:
        return Result(0, history, ridge, 0, 0, 0, 0)

    train = np.asarray(train_x)
    test = np.asarray(test_x)
    y = np.asarray(train_y)
    actual = np.asarray(test_y)

    mean = train.mean(0)
    scale = train.std(0)
    scale[scale == 0] = 1
    X = np.column_stack((np.ones(len(train)), (train-mean)/scale))
    V = np.column_stack((np.ones(len(test)), (test-mean)/scale))
    reg = np.eye(X.shape[1]); reg[0,0] = 0
    coef = np.linalg.solve(X.T @ X + ridge * reg, X.T @ y)
    pred = V @ coef

    shuffled = test.copy()
    np.random.default_rng(390001).shuffle(shuffled)
    sp = np.column_stack((np.ones(len(shuffled)), (shuffled-mean)/scale)) @ coef

    return Result(len(actual), history, ridge,
                  len(actual), float(np.mean(np.abs(actual))),
                  float(np.mean(np.abs(actual-pred))),
                  float(np.mean(np.abs(actual-sp))))


def main():
    print("GENESIS-2.13 temporal-compression regularization sweep")
    for seed in (390001, 390002, 390003):
        records = collect(seed)
        for history in (2, 3, 5):
            for ridge in (1e-3, 1e-2, 1e-1, 1.0, 10.0, 100.0):
                r = evaluate(records, history, ridge)
                print(seed, history, ridge, r.samples,
                      f"{r.zero_mae:.15g}", f"{r.state_mae:.15g}",
                      f"{r.shuffled_mae:.15g}", f"{r.improvement:.15g}")


if __name__ == "__main__":
    main()
