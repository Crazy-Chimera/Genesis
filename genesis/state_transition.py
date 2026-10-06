from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

from .memory import MemoryRecord
from .state_innovation import STATE_FEATURES


@dataclass(frozen=True)
class TransitionFeatureSpec:
    name: str
    width: int


TRANSITION_FEATURES = tuple(
    TransitionFeatureSpec(spec.name, 4) for spec in STATE_FEATURES
)
TRANSITION_WIDTH = sum(spec.width for spec in TRANSITION_FEATURES)


def transition_state(previous: MemoryRecord, current: MemoryRecord) -> tuple[float, ...]:
    values: list[float] = []

    for spec in STATE_FEATURES:
        before = np.asarray(spec.feature(previous), dtype=np.float64)
        after = np.asarray(spec.feature(current), dtype=np.float64)

        if before.shape != after.shape:
            raise ValueError(f"feature shape changed for {spec.name}")

        delta = after - before
        values.extend(
            (
                float(np.mean(delta)),
                float(np.mean(np.abs(delta))),
                float(np.linalg.norm(delta)),
                float(np.max(np.abs(delta))),
            )
        )

    return tuple(values)


@dataclass(frozen=True)
class StateTransitionEvaluationResult:
    samples: int
    zero_mae: float
    transition_mae: float
    shuffled_mae: float
    heldout_start_tick: int

    @property
    def improvement(self) -> float:
        return self.zero_mae - self.transition_mae

    @property
    def beats_zero(self) -> bool:
        return self.transition_mae < self.zero_mae

    @property
    def beats_shuffled(self) -> bool:
        return self.transition_mae < self.shuffled_mae


class StateTransitionPredictor:
    """Predict next coherence innovation from compact observer-state transitions."""

    def __init__(
        self,
        train_fraction: float = 0.5,
        ridge: float = 1e-6,
        require_consecutive: bool = True,
    ) -> None:
        if not 0.0 < train_fraction < 1.0:
            raise ValueError("train_fraction must be between 0 and 1")
        if ridge < 0.0:
            raise ValueError("ridge must be >= 0")
        self.train_fraction = train_fraction
        self.ridge = ridge
        self.require_consecutive = require_consecutive

    def evaluate(
        self, records: Iterable[MemoryRecord]
    ) -> StateTransitionEvaluationResult:
        ordered = sorted(records, key=lambda item: (item.tick, item.identity))
        if not ordered:
            return StateTransitionEvaluationResult(0, 0.0, 0.0, 0.0, 0)

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
            for index in range(1, len(items) - 1):
                previous = items[index - 1]
                current = items[index]
                target = items[index + 1]

                ticks = (previous.tick, current.tick, target.tick)
                if self.require_consecutive and (
                    ticks[1] != ticks[0] + 1 or ticks[2] != ticks[1] + 1
                ):
                    continue

                try:
                    row = transition_state(previous, current)
                except ValueError:
                    # Observer features can be undefined at lifecycle boundaries.
                    # Exclude that transition rather than coercing a missing state.
                    continue
                if len(row) != TRANSITION_WIDTH:
                    continue

                delta = target.coherence - current.coherence
                if target.tick < heldout:
                    train_x.append(row)
                    train_y.append(delta)
                else:
                    test_x.append(row)
                    test_y.append(delta)

        if not train_x or not test_x:
            return StateTransitionEvaluationResult(
                0, 0.0, 0.0, 0.0, heldout
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
        prediction = np.column_stack(
            (np.ones(len(test)), (test - mean) / scale)
        ) @ coefficients

        shuffled = test.copy()
        np.random.default_rng(390001).shuffle(shuffled)
        shuffled_prediction = np.column_stack(
            (np.ones(len(shuffled)), (shuffled - mean) / scale)
        ) @ coefficients

        actual = np.asarray(test_y, dtype=np.float64)

        return StateTransitionEvaluationResult(
            samples=len(actual),
            zero_mae=float(np.mean(np.abs(actual))),
            transition_mae=float(np.mean(np.abs(actual - prediction))),
            shuffled_mae=float(np.mean(np.abs(actual - shuffled_prediction))),
            heldout_start_tick=heldout,
        )
