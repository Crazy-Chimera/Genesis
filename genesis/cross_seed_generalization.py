from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

import numpy as np

from .memory import MemoryRecord
from .state_innovation import STATE_FEATURES_WITH_COMBINED, combined_state


@dataclass(frozen=True)
class CrossSeedGeneralizationResult:
    train_seeds: tuple[int, ...]
    target_seed: int
    history_length: int
    samples: int
    zero_mae: float
    pooled_mae: float
    shuffled_mae: float

    @property
    def improvement(self) -> float:
        return self.zero_mae - self.pooled_mae

    @property
    def beats_zero(self) -> bool:
        return self.pooled_mae < self.zero_mae

    @property
    def beats_shuffled(self) -> bool:
        return self.pooled_mae < self.shuffled_mae


def _windows(records: Iterable[MemoryRecord], history_length: int):
    groups: dict[int, list[MemoryRecord]] = {}
    for item in records:
        groups.setdefault(item.identity, []).append(item)

    rows = []
    for items in groups.values():
        items.sort(key=lambda x: x.tick)
        for i in range(history_length, len(items)):
            window = items[i-history_length:i]
            target = items[i]
            ticks = [x.tick for x in window] + [target.tick]
            if any(ticks[j + 1] != ticks[j] + 1 for j in range(len(ticks) - 1)):
                continue
            states = [np.asarray(combined_state(x), dtype=float) for x in window]\n            expected_width = next(\n                spec.width for spec in STATE_FEATURES_WITH_COMBINED\n                if spec.name == "combined"\n            )\n            if any(state.shape != (expected_width,) for state in states):\n                continue\n            rows.append((\n                target.tick,\n                states,\n                target.coherence - window[-1].coherence,\n            ))
    return sorted(rows, key=lambda x: x[0])


def _split(records: Iterable[MemoryRecord], history_length: int, fraction: float = 0.5):
    rows = _windows(records, history_length)
    if not rows:
        return [], [], [], []
    cutoff = rows[0][0] + max(1, int((rows[-1][0] - rows[0][0]) * fraction))
    train = [r for r in rows if r[0] < cutoff]
    test = [r for r in rows if r[0] >= cutoff]
    return train, test


class CrossSeedGeneralizationPredictor:
    """Train on pooled source seeds and evaluate once on an unseen target seed."""

    def __init__(self, history_length: int = 2, ridge: float = 1e-6):
        if history_length < 2:
            raise ValueError("history_length must be >= 2")
        if ridge < 0:
            raise ValueError("ridge must be >= 0")
        self.history_length = history_length
        self.ridge = ridge

    def evaluate(
        self,
        records_by_seed: dict[int, Sequence[MemoryRecord]],
        train_seeds: Sequence[int],
        target_seed: int,
    ) -> CrossSeedGeneralizationResult:
        if target_seed in train_seeds:
            raise ValueError("target_seed must not be in train_seeds")
        if not train_seeds:
            raise ValueError("train_seeds must not be empty")
        if target_seed not in records_by_seed or any(s not in records_by_seed for s in train_seeds):
            raise ValueError("records missing for requested seed")

        train_rows = []
        for seed in train_seeds:
            train_rows.extend(_split(records_by_seed[seed], self.history_length)[0])
        test_rows = _split(records_by_seed[target_seed], self.history_length)[1]
        if not train_rows or not test_rows:
            return CrossSeedGeneralizationResult(
                tuple(train_seeds), target_seed, self.history_length, 0, 0.0, 0.0, 0.0
            )

        def flatten(rows):
            return np.asarray([np.concatenate(row[1]) for row in rows], dtype=float)

        train = flatten(train_rows)
        test = flatten(test_rows)
        y = np.asarray([row[2] for row in train_rows], dtype=float)
        actual = np.asarray([row[2] for row in test_rows], dtype=float)

        mean = train.mean(0)
        scale = train.std(0)
        scale[scale == 0] = 1.0
        x = (train - mean) / scale
        v = (test - mean) / scale

        design = np.column_stack((np.ones(len(x)), x))
        reg = np.eye(design.shape[1])
        reg[0, 0] = 0.0
        coef = np.linalg.solve(
            design.T @ design + self.ridge * reg,
            design.T @ y,
        )
        pred = np.column_stack((np.ones(len(v)), v)) @ coef

        shuffled = v.copy()
        np.random.default_rng(390001).shuffle(shuffled)
        shuffled_pred = np.column_stack((np.ones(len(shuffled)), shuffled)) @ coef

        return CrossSeedGeneralizationResult(
            tuple(train_seeds),
            target_seed,
            self.history_length,
            len(actual),
            float(np.mean(np.abs(actual))),
            float(np.mean(np.abs(actual - pred))),
            float(np.mean(np.abs(actual - shuffled_pred))),
        )
