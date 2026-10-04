from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

from .memory import MemoryRecord
from .state_innovation import combined_state, STATE_FEATURES_WITH_COMBINED


@dataclass(frozen=True)
class DirectTransferResult:
    source_seed: int
    target_seed: int
    history_length: int
    samples: int
    zero_mae: float
    transfer_mae: float
    shuffled_mae: float

    @property
    def improvement(self) -> float:
        return self.zero_mae - self.transfer_mae

    @property
    def beats_zero(self) -> bool:
        return self.transfer_mae < self.zero_mae

    @property
    def beats_shuffled(self) -> bool:
        return self.transfer_mae < self.shuffled_mae


def _windows(records: Iterable[MemoryRecord], history_length: int):
    groups: dict[int, list[MemoryRecord]] = {}
    for item in records:
        groups.setdefault(item.identity, []).append(item)
    width = next(s.width for s in STATE_FEATURES_WITH_COMBINED if s.name == "combined")
    rows = []
    for items in groups.values():
        items.sort(key=lambda x: x.tick)
        for i in range(history_length, len(items)):
            window = items[i-history_length:i]
            target = items[i]
            ticks = [x.tick for x in window] + [target.tick]
            if any(ticks[j + 1] != ticks[j] + 1 for j in range(len(ticks) - 1)):
                continue
            states = [np.asarray(combined_state(x), dtype=float) for x in window]
            if any(state.ndim != 1 or state.size != width for state in states):
                continue
            rows.append((target.tick, states, target.coherence - window[-1].coherence))
    return sorted(rows, key=lambda x: x[0])


def _split(records: Iterable[MemoryRecord], history_length: int, fraction: float):
    rows = _windows(records, history_length)
    if not rows:
        return [], [], [], []
    ticks = [row[0] for row in rows]
    cutoff = ticks[0] + max(1, int((ticks[-1] - ticks[0]) * fraction))
    train = [row for row in rows if row[0] < cutoff]
    test = [row for row in rows if row[0] >= cutoff]
    return (
        [r[1] for r in train], [r[2] for r in train],
        [r[1] for r in test], [r[2] for r in test],
    )


class DirectStateTransferPredictor:
    """Train directly on the 193D combined state on one seed and test on another."""

    def __init__(self, history_length: int = 2, ridge: float = 1e-6):
        if history_length < 2:
            raise ValueError("history_length must be >= 2")
        if ridge < 0:
            raise ValueError("ridge must be >= 0")
        self.history_length = history_length
        self.ridge = ridge

    def evaluate(self, source_records, target_records, source_seed, target_seed):
        train_w, train_y, _, _ = _split(source_records, self.history_length, 0.5)
        _, _, test_w, test_y = _split(target_records, self.history_length, 0.5)
        x = np.asarray([np.asarray(w).reshape(-1) for w in train_w], dtype=float)
        v = np.asarray([np.asarray(w).reshape(-1) for w in test_w], dtype=float)
        y = np.asarray(train_y, dtype=float)
        actual = np.asarray(test_y, dtype=float)

        mean = x.mean(0)
        scale = x.std(0)
        scale[scale == 0] = 1
        xn = (x - mean) / scale
        vn = (v - mean) / scale
        design = np.column_stack((np.ones(len(xn)), xn))
        reg = np.eye(design.shape[1])
        reg[0, 0] = 0
        coef = np.linalg.solve(
            design.T @ design + self.ridge * reg,
            design.T @ y,
        )
        pred = np.column_stack((np.ones(len(vn)), vn)) @ coef
        shuffled = vn.copy()
        np.random.default_rng(390001).shuffle(shuffled)
        shuffled_pred = np.column_stack((np.ones(len(shuffled)), shuffled)) @ coef

        return DirectTransferResult(
            source_seed, target_seed, self.history_length, len(actual),
            float(np.mean(np.abs(actual))),
            float(np.mean(np.abs(actual - pred))),
            float(np.mean(np.abs(actual - shuffled_pred))),
        )
