from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .rule_distribution import rule_distribution_features


def rule_transition_features(
    previous_phase: np.ndarray,
    current_phase: np.ndarray,
    omega: np.ndarray,
    coupling: float,
) -> tuple[float, ...]:
    """Return the change in local update-rule distribution between two ticks."""
    previous = np.asarray(
        rule_distribution_features(previous_phase, omega, coupling),
        dtype=np.float64,
    )
    current = np.asarray(
        rule_distribution_features(current_phase, omega, coupling),
        dtype=np.float64,
    )
    delta = current - previous
    return tuple(float(value) for value in delta)


@dataclass(frozen=True)
class RuleTransitionResult:
    samples: int
    zero_mae: float
    transition_mae: float
    shuffled_mae: float

    @property
    def improvement(self) -> float:
        return self.zero_mae - self.transition_mae

    @property
    def beats_zero(self) -> bool:
        return self.transition_mae < self.zero_mae

    @property
    def beats_shuffled(self) -> bool:
        return self.transition_mae < self.shuffled_mae


class RuleTransitionPredictor:
    """Predict coherence innovation from local rule-distribution change."""

    def __init__(self, ridge: float = 1e-6) -> None:
        if ridge < 0.0:
            raise ValueError("ridge must be >= 0")
        self.ridge = ridge

    def fit_predict(self, train, test) -> RuleTransitionResult:
        if not train or not test:
            return RuleTransitionResult(0, 0.0, 0.0, 0.0)

        x = np.asarray([row[0] for row in train], dtype=np.float64)
        y = np.asarray([row[1] for row in train], dtype=np.float64)
        v = np.asarray([row[0] for row in test], dtype=np.float64)
        actual = np.asarray([row[1] for row in test], dtype=np.float64)

        mean = x.mean(axis=0)
        scale = x.std(axis=0)
        scale[scale == 0.0] = 1.0

        xn = (x - mean) / scale
        vn = (v - mean) / scale

        design = np.column_stack((np.ones(len(xn)), xn))
        regularizer = np.eye(design.shape[1])
        regularizer[0, 0] = 0.0
        coef = np.linalg.solve(
            design.T @ design + self.ridge * regularizer,
            design.T @ y,
        )

        pred = np.column_stack((np.ones(len(vn)), vn)) @ coef

        shuffled = vn.copy()
        np.random.default_rng(390001).shuffle(shuffled)
        shuffled_pred = np.column_stack((np.ones(len(shuffled)), shuffled)) @ coef

        return RuleTransitionResult(
            len(actual),
            float(np.mean(np.abs(actual))),
            float(np.mean(np.abs(actual - pred))),
            float(np.mean(np.abs(actual - shuffled_pred))),
        )
