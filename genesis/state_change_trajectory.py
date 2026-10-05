from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

from .memory import MemoryRecord
from .state_innovation import STATE_FEATURES_WITH_COMBINED, StateFeatureSpec


@dataclass(frozen=True)
class StateChangeTrajectoryEvaluationResult:
    samples: int
    zero_mae: float
    trajectory_mae: float
    shuffled_mae: float
    heldout_start_tick: int
    feature_name: str
    history_length: int

    @property
    def improvement(self) -> float:
        return self.zero_mae - self.trajectory_mae

    @property
    def beats_zero(self) -> bool:
        return self.trajectory_mae < self.zero_mae

    @property
    def beats_shuffled(self) -> bool:
        return self.trajectory_mae < self.shuffled_mae


class StateChangeTrajectoryPredictor:
    """Predict next coherence innovation from a trajectory of non-coherence state changes."""

    def __init__(
        self,
        feature_name: str = "combined",
        history_length: int = 3,
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
        matches = [
            spec for spec in STATE_FEATURES_WITH_COMBINED
            if spec.name == feature_name
        ]
        if not matches:
            raise ValueError(f"unknown state feature: {feature_name}")
        self.spec: StateFeatureSpec = matches[0]
        self.history_length = history_length
        self.train_fraction = train_fraction
        self.ridge = ridge
        self.require_consecutive = require_consecutive

    def evaluate(
        self, records: Iterable[MemoryRecord]
    ) -> StateChangeTrajectoryEvaluationResult:
        ordered = sorted(records, key=lambda item: (item.tick, item.identity))
        if not ordered:
            return StateChangeTrajectoryEvaluationResult(
                0, 0.0, 0.0, 0.0, 0, self.spec.name, self.history_length
            )

        min_tick, max_tick = ordered[0].tick, ordered[-1].tick
        heldout = min_tick + max(1, int((max_tick - min_tick) * self.train_fraction))
        groups: dict[int, list[MemoryRecord]] = {}
        for item in ordered:
            groups.setdefault(item.identity, []).append(item)

        train_x: list[tuple[float, ...]] = []
        train_y: list[float] = []
        test_x: list[tuple[float, ...]] = []
        test_y: list[float] = []

        for items in groups.values():
            items.sort(key=lambda item: item.tick)
            states = [
                np.asarray(self.spec.feature(item), dtype=np.float64)
                for item in items
            ]
            for index in range(1, len(items)):
                current = items[index]
                previous = items[index - 1]
                if (
                    self.require_consecutive
                    and current.tick != previous.tick + 1
                ):
                    continue
                if (
                    len(states[index]) != self.spec.width
                    or len(states[index - 1]) != self.spec.width
                ):
                    continue
                delta = states[index] - states[index - 1]
                target = current
                change_rows: list[np.ndarray] = [delta]
                if len(change_rows) < 1:
                    continue
                if index < self.history_length:
                    continue
                history_changes: list[np.ndarray] = []
                valid = True
                for j in range(index - self.history_length + 1, index + 1):
                    if items[j].tick != items[j - 1].tick + 1:
                        valid = False
                        break
                    history_changes.append(states[j] - states[j - 1])
                if not valid:
                    continue
                row = tuple(float(value) for change in history_changes for value in change)
                target_delta = target.coherence - previous.coherence
                if target.tick < heldout:
                    train_x.append(row)
                    train_y.append(target_delta)
                else:
                    test_x.append(row)
                    test_y.append(target_delta)

        if not train_x or not test_x:
            return StateChangeTrajectoryEvaluationResult(
                0, 0.0, 0.0, 0.0, heldout, self.spec.name, self.history_length
            )

        train = np.asarray(train_x, dtype=np.float64)
        test = np.asarray(test_x, dtype=np.float64)
        target = np.asarray(train_y, dtype=np.float64)
        mean = train.mean(axis=0)
        scale = train.std(axis=0)
        scale[scale == 0.0] = 1.0
        design = np.column_stack((np.ones(len(train)), (train - mean) / scale))
        regularizer = np.eye(design.shape[1])
        regularizer[0, 0] = 0.0
        coefficients = np.linalg.solve(
            design.T @ design + self.ridge * regularizer,
            design.T @ target,
        )
        prediction = np.column_stack(
            (np.ones(len(test)), (test - mean) / scale)
        ) @ coefficients

        shuffled = test.copy()
        np.random.default_rng(390001).shuffle(shuffled)
        shuffled_prediction = np.column_stack(
            (np.ones(len(shuffled)), (shuffled - mean) / scale)
        ) @ coefficients
        actual = np.asarray(test_y, dtype=np.float64)

        return StateChangeTrajectoryEvaluationResult(
            len(actual),
            float(np.mean(np.abs(actual))),
            float(np.mean(np.abs(actual - prediction))),
            float(np.mean(np.abs(actual - shuffled_prediction))),
            heldout,
            self.spec.name,
            self.history_length,
        )
