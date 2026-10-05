from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

from .memory import MemoryRecord
from .state_innovation import STATE_FEATURES_WITH_COMBINED, StateFeatureSpec


@dataclass(frozen=True)
class StateTrajectoryGeometryResult:
    samples: int
    zero_mae: float
    geometry_mae: float
    shuffled_mae: float
    heldout_start_tick: int
    feature_name: str
    history_length: int

    @property
    def improvement(self) -> float:
        return self.zero_mae - self.geometry_mae

    @property
    def beats_zero(self) -> bool:
        return self.geometry_mae < self.zero_mae

    @property
    def beats_shuffled(self) -> bool:
        return self.geometry_mae < self.shuffled_mae


def _normalize_state(values: tuple[float, ...]) -> np.ndarray:
    vector = np.asarray(values, dtype=np.float64)
    scale = float(vector.std())
    if scale == 0.0:
        return np.zeros_like(vector)
    return (vector - float(vector.mean())) / scale


def trajectory_geometry(
    records: list[MemoryRecord],
    spec: StateFeatureSpec,
) -> tuple[float, ...]:
    states = [
        _normalize_state(tuple(float(v) for v in spec.feature(record)))
        for record in records
    ]
    velocities = [states[i + 1] - states[i] for i in range(len(states) - 1)]
    velocity_norms = [float(np.linalg.norm(v)) for v in velocities]

    features = [
        float(np.mean(velocity_norms)),
        float(np.std(velocity_norms)),
        float(np.max(velocity_norms)),
    ]

    if velocities:
        features.extend(
            [
                float(np.mean(velocities[-1])),
                float(np.std(velocities[-1])),
                float(np.linalg.norm(velocities[-1])),
            ]
        )
    else:
        features.extend([0.0, 0.0, 0.0])

    if len(states) >= 2:
        cosines = []
        for left, right in zip(states[:-1], states[1:]):
            denom = float(np.linalg.norm(left) * np.linalg.norm(right))
            cosines.append(float(left @ right / denom) if denom else 0.0)
        features.extend([float(np.mean(cosines)), float(cosines[-1])])
    else:
        features.extend([0.0, 0.0])

    if len(velocities) >= 2:
        accelerations = [
            velocities[i + 1] - velocities[i]
            for i in range(len(velocities) - 1)
        ]
        acceleration_norms = [float(np.linalg.norm(a)) for a in accelerations]
        features.extend(
            [
                float(np.mean(acceleration_norms)),
                float(np.std(acceleration_norms)),
                float(acceleration_norms[-1]),
            ]
        )
    else:
        features.extend([0.0, 0.0, 0.0])

    return tuple(features)


class StateTrajectoryGeometryPredictor:
    """Predict next coherence innovation from compact state-trajectory geometry."""

    def __init__(
        self,
        feature_name: str = "combined",
        history_length: int = 3,
        train_fraction: float = 0.5,
        ridge: float = 1e-3,
        require_consecutive: bool = True,
    ) -> None:
        if history_length < 2:
            raise ValueError("history_length must be >= 2")
        if not 0.0 < train_fraction < 1.0:
            raise ValueError("train_fraction must be between 0 and 1")
        if ridge < 0.0:
            raise ValueError("ridge must be >= 0")
        matches = [s for s in STATE_FEATURES_WITH_COMBINED if s.name == feature_name]
        if not matches:
            raise ValueError(f"unknown state feature: {feature_name}")
        self.spec = matches[0]
        self.history_length = history_length
        self.train_fraction = train_fraction
        self.ridge = ridge
        self.require_consecutive = require_consecutive

    def evaluate(self, records: Iterable[MemoryRecord]) -> StateTrajectoryGeometryResult:
        ordered = sorted(records, key=lambda x: (x.tick, x.identity))
        if not ordered:
            return StateTrajectoryGeometryResult(
                0, 0.0, 0.0, 0.0, 0, self.spec.name, self.history_length
            )

        lo, hi = ordered[0].tick, ordered[-1].tick
        heldout = lo + max(1, int((hi - lo) * self.train_fraction))
        groups: dict[int, list[MemoryRecord]] = {}
        for item in ordered:
            groups.setdefault(item.identity, []).append(item)

        train_x: list[tuple[float, ...]] = []
        train_y: list[float] = []
        test_x: list[tuple[float, ...]] = []
        test_y: list[float] = []

        for items in groups.values():
            items.sort(key=lambda x: x.tick)
            for index in range(self.history_length, len(items)):
                window = items[index - self.history_length:index]
                target = items[index]
                ticks = [x.tick for x in window] + [target.tick]
                if self.require_consecutive and any(
                    ticks[j + 1] != ticks[j] + 1 for j in range(len(ticks) - 1)
                ):
                    continue
                row = trajectory_geometry(window, self.spec)
                delta = target.coherence - window[-1].coherence
                if target.tick < heldout:
                    train_x.append(row)
                    train_y.append(delta)
                else:
                    test_x.append(row)
                    test_y.append(delta)

        if not train_x or not test_x:
            return StateTrajectoryGeometryResult(
                0, 0.0, 0.0, 0.0, heldout, self.spec.name, self.history_length
            )

        train = np.asarray(train_x, dtype=np.float64)
        test = np.asarray(test_x, dtype=np.float64)
        target = np.asarray(train_y, dtype=np.float64)
        mean = train.mean(axis=0)
        scale = train.std(axis=0)
        scale[scale == 0.0] = 1.0

        x = np.column_stack((np.ones(len(train)), (train - mean) / scale))
        v = np.column_stack((np.ones(len(test)), (test - mean) / scale))
        reg = np.eye(x.shape[1])
        reg[0, 0] = 0.0
        coef = np.linalg.solve(x.T @ x + self.ridge * reg, x.T @ target)
        prediction = v @ coef

        shuffled = test.copy()
        np.random.default_rng(390001).shuffle(shuffled)
        shuffled_prediction = np.column_stack(
            (np.ones(len(shuffled)), (shuffled - mean) / scale)
        ) @ coef

        actual = np.asarray(test_y, dtype=np.float64)
        return StateTrajectoryGeometryResult(
            len(actual),
            float(np.mean(np.abs(actual))),
            float(np.mean(np.abs(actual - prediction))),
            float(np.mean(np.abs(actual - shuffled_prediction))),
            heldout,
            self.spec.name,
            self.history_length,
        )
