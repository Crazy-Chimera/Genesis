from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
import numpy as np

from .memory import MemoryRecord
from .state_innovation import STATE_FEATURES_WITH_COMBINED


@dataclass(frozen=True)
class StateDirectionEvaluationResult:
    samples: int
    majority_accuracy: float
    direction_accuracy: float
    shuffled_accuracy: float
    heldout_start_tick: int
    feature_name: str

    @property
    def improvement(self) -> float:
        return self.direction_accuracy - self.majority_accuracy

    @property
    def beats_majority(self) -> bool:
        return self.direction_accuracy > self.majority_accuracy

    @property
    def beats_shuffled(self) -> bool:
        return self.direction_accuracy > self.shuffled_accuracy


class StateDirectionPredictor:
    """Predict the sign of next coherence innovation from non-coherence state."""

    def __init__(
        self,
        feature_name: str = "combined",
        train_fraction: float = 0.5,
        ridge: float = 1e-6,
        require_consecutive: bool = True,
    ) -> None:
        if not 0.0 < train_fraction < 1.0:
            raise ValueError("train_fraction must be between 0 and 1")
        if ridge < 0.0:
            raise ValueError("ridge must be >= 0")
        matches = [s for s in STATE_FEATURES_WITH_COMBINED if s.name == feature_name]
        if not matches:
            raise ValueError(f"unknown state feature: {feature_name}")
        self.spec = matches[0]
        self.train_fraction = train_fraction
        self.ridge = ridge
        self.require_consecutive = require_consecutive

    def evaluate(self, records: Iterable[MemoryRecord]) -> StateDirectionEvaluationResult:
        ordered = sorted(records, key=lambda item: (item.tick, item.identity))
        if not ordered:
            return StateDirectionEvaluationResult(0, 0.0, 0.0, 0.0, 0, self.spec.name)

        min_tick, max_tick = ordered[0].tick, ordered[-1].tick
        heldout = min_tick + max(1, int((max_tick - min_tick) * self.train_fraction))
        groups: dict[int, list[MemoryRecord]] = {}
        for item in ordered:
            groups.setdefault(item.identity, []).append(item)

        train_x, train_y, test_x, test_y = [], [], [], []
        for items in groups.values():
            items.sort(key=lambda item: item.tick)
            for i in range(len(items) - 1):
                current, target = items[i], items[i + 1]
                if self.require_consecutive and target.tick != current.tick + 1:
                    continue
                row = tuple(float(v) for v in self.spec.feature(current))
                if len(row) != self.spec.width:
                    continue
                delta = target.coherence - current.coherence
                label = 1.0 if delta > 0.0 else 0.0
                if target.tick < heldout:
                    train_x.append(row)
                    train_y.append(label)
                else:
                    test_x.append(row)
                    test_y.append(label)

        if not train_x or not test_x:
            return StateDirectionEvaluationResult(0, 0.0, 0.0, 0.0, heldout, self.spec.name)

        train = np.asarray(train_x, dtype=np.float64)
        y = np.asarray(train_y, dtype=np.float64)
        test = np.asarray(test_x, dtype=np.float64)
        actual = np.asarray(test_y, dtype=np.float64)

        mean = train.mean(axis=0)
        scale = train.std(axis=0)
        scale[scale == 0.0] = 1.0
        x = (train - mean) / scale
        v = (test - mean) / scale
        design = np.column_stack((np.ones(len(x)), x))
        reg = np.eye(design.shape[1])
        reg[0, 0] = 0.0
        coef = np.linalg.solve(design.T @ design + self.ridge * reg, design.T @ y)

        prediction = (np.column_stack((np.ones(len(v)), v)) @ coef >= 0.5).astype(float)

        shuffled = test.copy()
        np.random.default_rng(390001).shuffle(shuffled)
        shuffled_prediction = (
            np.column_stack((np.ones(len(shuffled)), (shuffled - mean) / scale)) @ coef >= 0.5
        ).astype(float)

        majority = max(float(np.mean(actual)), 1.0 - float(np.mean(actual)))
        return StateDirectionEvaluationResult(
            samples=len(actual),
            majority_accuracy=majority,
            direction_accuracy=float(np.mean(prediction == actual)),
            shuffled_accuracy=float(np.mean(shuffled_prediction == actual)),
            heldout_start_tick=heldout,
            feature_name=self.spec.name,
        )
