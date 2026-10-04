from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

from .memory import MemoryRecord
from .state_innovation import combined_state


@dataclass(frozen=True)
class CrossSeedTrajectoryResult:
    samples: int
    zero_mae: float
    transfer_mae: float
    shuffled_mae: float
    train_seed: int
    test_seed: int
    history_length: int
    heldout_start_tick: int

    @property
    def improvement(self) -> float:
        return self.zero_mae - self.transfer_mae

    @property
    def beats_zero(self) -> bool:
        return self.transfer_mae < self.zero_mae

    @property
    def beats_shuffled(self) -> bool:
        return self.transfer_mae < self.shuffled_mae


class CrossSeedTrajectoryPredictor:
    """Train on one seed and test a non-coherence trajectory predictor on another."""

    def __init__(
        self,
        history_length: int = 2,
        train_fraction: float = 0.5,
        ridge: float = 1e-6,
        require_consecutive: bool = True,
    ) -> None:
        if history_length < 2:
            raise ValueError("history_length must be >= 2")
        if not 0.0 < train_fraction < 1.0:
            raise ValueError("train_fraction must be between 0 and 1")
        if ridge < 0.0:
            raise ValueError("ridge must be >= 0")
        self.history_length = history_length
        self.train_fraction = train_fraction
        self.ridge = ridge
        self.require_consecutive = require_consecutive

    @staticmethod
    def _windows(records: Iterable[MemoryRecord], history_length: int, require_consecutive: bool):
        ordered = sorted(records, key=lambda item: (item.tick, item.identity))
        groups: dict[int, list[MemoryRecord]] = {}
        for item in ordered:
            groups.setdefault(item.identity, []).append(item)

        for items in groups.values():
            items.sort(key=lambda item: item.tick)
            for i in range(history_length, len(items)):
                window = items[i - history_length:i]
                target = items[i]
                ticks = [item.tick for item in window] + [target.tick]
                if require_consecutive and any(
                    ticks[j + 1] != ticks[j] + 1 for j in range(len(ticks) - 1)
                ):
                    continue
                row = tuple(
                    value
                    for item in window
                    for value in combined_state(item)
                )
                yield row, target.coherence - window[-1].coherence, target.tick

    def evaluate(
        self,
        train_records: Iterable[MemoryRecord],
        test_records: Iterable[MemoryRecord],
        *,
        train_seed: int = 0,
        test_seed: int = 0,
    ) -> CrossSeedTrajectoryResult:
        train_all = list(train_records)
        test_all = list(test_records)
        if not train_all or not test_all:
            return CrossSeedTrajectoryResult(
                0, 0.0, 0.0, 0.0, train_seed, test_seed,
                self.history_length, 0,
            )

        train_ticks = [item.tick for item in train_all]
        test_ticks = [item.tick for item in test_all]
        train_holdout = min(train_ticks) + max(
            1, int((max(train_ticks) - min(train_ticks)) * self.train_fraction)
        )
        test_holdout = min(test_ticks) + max(
            1, int((max(test_ticks) - min(test_ticks)) * self.train_fraction)
        )

        train_x: list[tuple[float, ...]] = []
        train_y: list[float] = []
        for row, target, tick in self._windows(
            train_all, self.history_length, self.require_consecutive
        ):
            if tick < train_holdout:
                train_x.append(row)
                train_y.append(target)

        test_x: list[tuple[float, ...]] = []
        test_y: list[float] = []
        for row, target, tick in self._windows(
            test_all, self.history_length, self.require_consecutive
        ):
            if tick >= test_holdout:
                test_x.append(row)
                test_y.append(target)

        if not train_x or not test_x:
            return CrossSeedTrajectoryResult(
                0, 0.0, 0.0, 0.0, train_seed, test_seed,
                self.history_length, test_holdout,
            )

        train = np.asarray(train_x, dtype=np.float64)
        target = np.asarray(train_y, dtype=np.float64)
        mean = train.mean(axis=0)
        scale = train.std(axis=0)
        scale[scale == 0.0] = 1.0

        design = np.column_stack(
            (np.ones(len(train)), (train - mean) / scale)
        )
        regularizer = np.eye(design.shape[1])
        regularizer[0, 0] = 0.0
        coefficients = np.linalg.solve(
            design.T @ design + self.ridge * regularizer,
            design.T @ target,
        )

        test = np.asarray(test_x, dtype=np.float64)
        actual = np.asarray(test_y, dtype=np.float64)
        prediction = np.column_stack(
            (np.ones(len(test)), (test - mean) / scale)
        ) @ coefficients

        shuffled = test.copy()
        np.random.default_rng(390001).shuffle(shuffled)
        shuffled_prediction = np.column_stack(
            (np.ones(len(shuffled)), (shuffled - mean) / scale)
        ) @ coefficients

        return CrossSeedTrajectoryResult(
            samples=len(actual),
            zero_mae=float(np.mean(np.abs(actual))),
            transfer_mae=float(np.mean(np.abs(actual - prediction))),
            shuffled_mae=float(np.mean(np.abs(actual - shuffled_prediction))),
            train_seed=train_seed,
            test_seed=test_seed,
            history_length=self.history_length,
            heldout_start_tick=test_holdout,
        )
