from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Sequence

import numpy as np

from .memory import MemoryRecord

StateFeature = Callable[[MemoryRecord], Sequence[float]]


@dataclass(frozen=True)
class StateInnovationEvaluationResult:
    samples: int
    zero_mae: float
    state_mae: float
    shuffled_mae: float
    heldout_start_tick: int
    feature_name: str

    @property
    def improvement(self) -> float:
        return self.zero_mae - self.state_mae

    @property
    def beats_zero(self) -> bool:
        return self.state_mae < self.zero_mae

    @property
    def beats_shuffled(self) -> bool:
        return self.state_mae < self.shuffled_mae


def structure_state(record: MemoryRecord) -> tuple[float, ...]:
    return (
        float(len(record.cells)),
        record.boundary_contrast,
        float(record.lifetime),
        float(record.persistence),
        record.overlap,
    )


def field_state(name: str) -> StateFeature:
    def feature(record: MemoryRecord) -> Sequence[float]:
        return getattr(record, name)
    return feature


@dataclass(frozen=True)
class StateFeatureSpec:
    name: str
    feature: StateFeature
    width: int


STATE_FEATURES = (
    StateFeatureSpec("structure", structure_state, 5),
    StateFeatureSpec("local_patch", field_state("local_patch"), 9),
    StateFeatureSpec("phase_patch", field_state("phase_patch"), 18),
    StateFeatureSpec("gradient_patch", field_state("gradient_patch"), 18),
    StateFeatureSpec("motion", field_state("motion"), 3),
    StateFeatureSpec("boundary_flux", field_state("boundary_flux"), 5),
    StateFeatureSpec("spatial_field", field_state("spatial_field"), 18),
    StateFeatureSpec("multiscale_field", field_state("multiscale_field"), 68),
    StateFeatureSpec("relational", field_state("relational"), 16),
    StateFeatureSpec("graph_relational", field_state("graph_relational"), 33),
)


class StateInnovationPredictor:
    """Predict next coherence change from the current non-coherence state."""

    def __init__(
        self,
        feature_name: str,
        train_fraction: float = 0.5,
        ridge: float = 1e-6,
        require_consecutive: bool = True,
    ) -> None:
        if not 0.0 < train_fraction < 1.0:
            raise ValueError("train_fraction must be between 0 and 1")
        if ridge < 0.0:
            raise ValueError("ridge must be >= 0")
        matches = [spec for spec in STATE_FEATURES if spec.name == feature_name]
        if not matches:
            raise ValueError(f"unknown state feature: {feature_name}")
        self.spec = matches[0]
        self.train_fraction = train_fraction
        self.ridge = ridge
        self.require_consecutive = require_consecutive

    def evaluate(self, records: Iterable[MemoryRecord]) -> StateInnovationEvaluationResult:
        ordered = sorted(records, key=lambda item: (item.tick, item.identity))
        if not ordered:
            return StateInnovationEvaluationResult(
                0, 0.0, 0.0, 0.0, 0, self.spec.name
            )

        min_tick, max_tick = ordered[0].tick, ordered[-1].tick
        heldout = min_tick + max(1, int((max_tick - min_tick) * self.train_fraction))
        by_identity: dict[int, list[MemoryRecord]] = {}
        for item in ordered:
            by_identity.setdefault(item.identity, []).append(item)

        train_x: list[tuple[float, ...]] = []
        train_y: list[float] = []
        test_x: list[tuple[float, ...]] = []
        test_y: list[float] = []

        for items in by_identity.values():
            items.sort(key=lambda item: item.tick)
            for index in range(len(items) - 1):
                current = items[index]
                target = items[index + 1]
                if self.require_consecutive and target.tick != current.tick + 1:
                    continue
                row = tuple(float(value) for value in self.spec.feature(current))
                if len(row) != self.spec.width:
                    continue
                delta = target.coherence - current.coherence
                if target.tick < heldout:
                    train_x.append(row)
                    train_y.append(delta)
                else:
                    test_x.append(row)
                    test_y.append(delta)

        if not train_x or not test_x:
            return StateInnovationEvaluationResult(
                0, 0.0, 0.0, 0.0, heldout, self.spec.name
            )

        train = np.asarray(train_x, dtype=np.float64)
        target = np.asarray(train_y, dtype=np.float64)
        mean = train.mean(axis=0)
        scale = train.std(axis=0)
        scale[scale == 0.0] = 1.0
        normalized = (train - mean) / scale
        design = np.column_stack((np.ones(len(train)), normalized))
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
        return StateInnovationEvaluationResult(
            samples=len(actual),
            zero_mae=float(np.mean(np.abs(actual))),
            state_mae=float(np.mean(np.abs(actual - prediction))),
            shuffled_mae=float(np.mean(np.abs(actual - shuffled_prediction))),
            heldout_start_tick=heldout,
            feature_name=self.spec.name,
        )
