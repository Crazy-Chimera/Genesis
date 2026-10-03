from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

from .memory import MemoryRecord


@dataclass(frozen=True)
class InnovationEvaluationResult:
    samples: int
    zero_mae: float
    innovation_mae: float
    shuffled_mae: float
    heldout_start_tick: int
    history_length: int

    @property
    def improvement(self) -> float:
        return self.zero_mae - self.innovation_mae

    @property
    def beats_zero(self) -> bool:
        return self.innovation_mae < self.zero_mae

    @property
    def beats_shuffled(self) -> bool:
        return self.innovation_mae < self.shuffled_mae


class InnovationPredictor:
    """Predict the next coherence change rather than coherence itself."""

    def __init__(
        self,
        history_length: int = 3,
        train_fraction: float = 0.5,
        ridge: float = 1e-6,
        require_consecutive: bool = True,
    ) -> None:
        if history_length < 1:
            raise ValueError("history_length must be >= 1")
        if not 0.0 < train_fraction < 1.0:
            raise ValueError("train_fraction must be between 0 and 1")
        if ridge < 0.0:
            raise ValueError("ridge must be >= 0")
        self.history_length = history_length
        self.train_fraction = train_fraction
        self.ridge = ridge
        self.require_consecutive = require_consecutive

    def evaluate(self, records: Iterable[MemoryRecord]) -> InnovationEvaluationResult:
        ordered = sorted(records, key=lambda item: (item.tick, item.identity))
        if not ordered:
            return InnovationEvaluationResult(0, 0.0, 0.0, 0.0, 0, self.history_length)

        min_tick, max_tick = ordered[0].tick, ordered[-1].tick
        heldout = min_tick + max(1, int((max_tick - min_tick) * self.train_fraction))
        by_identity: dict[int, list[MemoryRecord]] = {}
        for item in ordered:
            by_identity.setdefault(item.identity, []).append(item)

        train_x: list[list[float]] = []
        train_y: list[float] = []
        test_x: list[list[float]] = []
        test_y: list[float] = []
        zero_errors: list[float] = []

        for items in by_identity.values():
            items.sort(key=lambda item: item.tick)
            for i in range(self.history_length, len(items)):
                window = items[i - self.history_length:i + 1]
                if self.require_consecutive and any(
                    window[j].tick + 1 != window[j + 1].tick
                    for j in range(len(window) - 1)
                ):
                    continue
                deltas = [
                    window[j + 1].coherence - window[j].coherence
                    for j in range(len(window) - 1)
                ]
                target = deltas[-1]
                features = deltas[:-1]
                if not features:
                    continue
                if window[-1].tick < heldout:
                    train_x.append(features)
                    train_y.append(target)
                else:
                    test_x.append(features)
                    test_y.append(target)
                    zero_errors.append(abs(target))

        if not train_x or not test_x:
            return InnovationEvaluationResult(0, 0.0, 0.0, 0.0, heldout, self.history_length)

        x = np.asarray(train_x, dtype=np.float64)
        y = np.asarray(train_y, dtype=np.float64)
        mean = x.mean(axis=0)
        scale = x.std(axis=0)
        scale[scale == 0.0] = 1.0
        x_norm = (x - mean) / scale
        design = np.column_stack((np.ones(len(x_norm)), x_norm))
        reg = np.eye(design.shape[1])
        reg[0, 0] = 0.0
        coef = np.linalg.solve(
            design.T @ design + self.ridge * reg,
            design.T @ y,
        )

        test = (np.asarray(test_x, dtype=np.float64) - mean) / scale
        prediction = np.column_stack((np.ones(len(test)), test)) @ coef

        shuffled = np.asarray(test_x, dtype=np.float64).copy()
        np.random.default_rng(390001).shuffle(shuffled)
        shuffled = (shuffled - mean) / scale
        shuffled_prediction = np.column_stack((np.ones(len(shuffled)), shuffled)) @ coef

        actual = np.asarray(test_y, dtype=np.float64)
        return InnovationEvaluationResult(
            samples=len(actual),
            zero_mae=float(np.mean(zero_errors)),
            innovation_mae=float(np.mean(np.abs(actual - prediction))),
            shuffled_mae=float(np.mean(np.abs(actual - shuffled_prediction))),
            heldout_start_tick=heldout,
            history_length=self.history_length,
        )
