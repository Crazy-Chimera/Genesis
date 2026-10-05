from __future__ import annotations

from dataclasses import dataclass
import numpy as np


def rule_invariant_features(
    phase: np.ndarray,
    omega: np.ndarray,
    coupling: float,
) -> tuple[float, ...]:
    """Return dimensionless observables derived directly from the PW-001 update rule."""
    p = np.asarray(phase, dtype=float)
    w = np.asarray(omega, dtype=float)
    deltas = (
        np.roll(p, 1, 0) - p,
        np.roll(p, -1, 0) - p,
        np.roll(p, 1, 1) - p,
        np.roll(p, -1, 1) - p,
    )
    local_coupling = sum(np.sin(delta) for delta in deltas) / 4.0
    forcing = coupling * local_coupling
    update = w + forcing

    omega_rms = float(np.sqrt(np.mean(w * w)))
    forcing_rms = float(np.sqrt(np.mean(forcing * forcing)))
    update_rms = float(np.sqrt(np.mean(update * update)))
    denom = max(omega_rms, 1e-15)
    total = max(omega_rms * omega_rms + forcing_rms * forcing_rms, 1e-30)

    return (
        forcing_rms / denom,
        update_rms / denom,
        float(np.mean(forcing * forcing)) / total,
        float(np.mean(w * forcing)) / total,
        float(np.mean(local_coupling * local_coupling)),
        float(np.mean(np.abs(local_coupling))),
    )


@dataclass(frozen=True)
class RuleInvariantResult:
    samples: int
    zero_mae: float
    invariant_mae: float
    shuffled_mae: float

    @property
    def improvement(self) -> float:
        return self.zero_mae - self.invariant_mae

    @property
    def beats_zero(self) -> bool:
        return self.invariant_mae < self.zero_mae

    @property
    def beats_shuffled(self) -> bool:
        return self.invariant_mae < self.shuffled_mae


class RuleInvariantPredictor:
    def __init__(self, ridge: float = 1e-6) -> None:
        if ridge < 0.0:
            raise ValueError("ridge must be >= 0")
        self.ridge = ridge

    def fit_predict(self, train, test) -> RuleInvariantResult:
        if not train or not test:
            return RuleInvariantResult(0, 0.0, 0.0, 0.0)

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

        return RuleInvariantResult(
            len(actual),
            float(np.mean(np.abs(actual))),
            float(np.mean(np.abs(actual - pred))),
            float(np.mean(np.abs(actual - shuffled_pred))),
        )
