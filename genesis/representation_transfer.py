from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

from .memory import MemoryRecord
from .state_innovation import combined_state


@dataclass(frozen=True)
class RepresentationTransferResult:
    source_seed: int
    target_seed: int
    components: int
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


def _split(records: Iterable[MemoryRecord], history_length: int, fraction: float):
    groups: dict[int, list[MemoryRecord]] = {}
    for item in records:
        groups.setdefault(item.identity, []).append(item)
    windows, targets = [], []
    for items in groups.values():
        items.sort(key=lambda x: x.tick)
        for i in range(history_length, len(items)):
            window = items[i-history_length:i]
            target = items[i]
            ticks = [x.tick for x in window] + [target.tick]
            if any(ticks[j+1] != ticks[j] + 1 for j in range(len(ticks)-1)):
                continue
            windows.append([np.asarray(combined_state(x), dtype=float) for x in window])
            targets.append(target.coherence - window[-1].coherence)
    cutoff = int(len(windows) * fraction)
    return windows[:cutoff], targets[:cutoff], windows[cutoff:], targets[cutoff:]


class RepresentationTransferPredictor:
    """Test a PCA representation learned on one seed on another seed."""

    def __init__(self, components=2, history_length=2, ridge=1e-6):
        if components < 1 or components > 193:
            raise ValueError("components must be between 1 and 193")
        if history_length < 2:
            raise ValueError("history_length must be >= 2")
        if ridge < 0:
            raise ValueError("ridge must be >= 0")
        self.components = components
        self.history_length = history_length
        self.ridge = ridge

    def fit_transform_basis(self, records):
        train, _, _, _ = _split(records, self.history_length, 0.5)
        states = np.asarray([state for w in train for state in w])
        mean = states.mean(0)
        scale = states.std(0)
        scale[scale == 0] = 1
        normalized = (states - mean) / scale
        cov = (normalized.T @ normalized) / max(1, len(normalized) - 1)
        values, vectors = np.linalg.eigh(cov)
        basis = vectors[:, np.argsort(values)[::-1][:self.components]]
        return mean, scale, basis

    def evaluate(self, source_records, target_records, source_seed, target_seed):
        mean, scale, basis = self.fit_transform_basis(source_records)

        def encode(windows):
            return np.asarray([
                ((np.asarray(w) - mean) / scale @ basis).reshape(-1)
                for w in windows
            ])

        train_w, train_y, _, _ = _split(source_records, self.history_length, 0.5)
        _, _, test_w, test_y = _split(target_records, self.history_length, 0.5)
        x = encode(train_w)
        v = encode(test_w)
        y = np.asarray(train_y)
        actual = np.asarray(test_y)

        xm, xs = x.mean(0), x.std(0)
        xs[xs == 0] = 1
        xn = (x-xm)/xs
        vn = (v-xm)/xs
        design = np.column_stack((np.ones(len(xn)), xn))
        reg = np.eye(design.shape[1]); reg[0,0] = 0
        coef = np.linalg.solve(design.T @ design + self.ridge*reg, design.T@y)
        pred = np.column_stack((np.ones(len(vn)), vn)) @ coef
        shuffled = vn.copy()
        np.random.default_rng(390001).shuffle(shuffled)
        sp = np.column_stack((np.ones(len(shuffled)), shuffled)) @ coef
        return RepresentationTransferResult(
            source_seed, target_seed, self.components, self.history_length,
            len(actual), float(np.mean(np.abs(actual))),
            float(np.mean(np.abs(actual-pred))),
            float(np.mean(np.abs(actual-sp))),
        )
