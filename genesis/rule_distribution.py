from __future__ import annotations

from dataclasses import dataclass
import numpy as np


QUANTILES = (0.05, 0.25, 0.5, 0.75, 0.95)


def rule_distribution_features(
    phase: np.ndarray,
    omega: np.ndarray,
    coupling: float,
) -> tuple[float, ...]:
    """Dimensionless distributional observables of the local PW-001 update rule."""
    p = np.asarray(phase, dtype=float)
    w = np.asarray(omega, dtype=float)
    deltas = (
        np.roll(p, 1, 0) - p,
        np.roll(p, -1, 0) - p,
        np.roll(p, 1, 1) - p,
        np.roll(p, -1, 1) - p,
    )
    local_coupling = sum(np.sin(delta) for delta in deltas) / 4.0
    omega_rms = max(float(np.sqrt(np.mean(w * w))), 1e-15)
    forcing = coupling * local_coupling / omega_rms
    update = (w + coupling * local_coupling) / omega_rms

    arrays = (
        local_coupling,
        forcing,
        update,
    )
    return tuple(
        float(value)
        for array in arrays
        for value in np.quantile(array, QUANTILES)
    )


@dataclass(frozen=True)
class RuleDistributionResult:
    samples: int
    zero_mae: float
    distribution_mae: float
    shuffled_mae: float

    @property
    def improvement(self) -> float:
        return self.zero_mae - self.distribution_mae

    @property
    def beats_zero(self) -> bool:
        return self.distribution_mae < self.zero_mae

    @property
    def beats_shuffled(self) -> bool:
        return self.distribution_mae < self.shuffled_mae


class RuleDistributionPredictor:
    def __init__(self, ridge: float = 1e-6) -> None:
        if ridge < 0.0:
            raise ValueError("ridge must be >= 0")
        self.ridge = ridge

    def fit_predict(self, train, test) -> RuleDistributionResult:
        if not train or not test:
            return RuleDistributionResult(0, 0.0, 0.0, 0.0)

        x = np.asarray([row[0] for row in train], dtype=float)
        y = np.asarray([row[1] for row in train], dtype=float)
        v = np.asarray([row[0] for row in test], dtype=float)
        actual = np.asarray([row[1] for row in test], dtype=float)

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

        return RuleDistributionResult(
            len(actual),
            float(np.mean(np.abs(actual))),
            float(np.mean(np.abs(actual - pred))),
            float(np.mean(np.abs(actual - shuffled_pred))),
        )
