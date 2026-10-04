from __future__ import annotations

from dataclasses import dataclass
import numpy as np


def rule_update_features(phase: np.ndarray, omega: np.ndarray, coupling: float) -> tuple[float, ...]:
    p = np.asarray(phase, dtype=float)
    w = np.asarray(omega, dtype=float)
    deltas = (
        np.roll(p, 1, 0) - p,
        np.roll(p, -1, 0) - p,
        np.roll(p, 1, 1) - p,
        np.roll(p, -1, 1) - p,
    )
    local_coupling = sum(np.sin(deltas)) / 4.0
    local_update = w + coupling * local_coupling
    centered = local_update - float(np.mean(local_update))
    return (
        float(np.mean(local_update)),
        float(np.std(local_update)),
        float(np.mean(np.abs(local_update))),
        float(np.mean(local_update * local_update)),
        float(np.mean(local_coupling * local_coupling)),
        float(np.mean(np.cos(deltas[0]) + np.cos(deltas[1]) + np.cos(deltas[2]) + np.cos(deltas[3])) / 4.0),
        float(np.mean(centered * local_coupling)),
        float(np.std(centered * local_coupling)),
    )


@dataclass(frozen=True)
class RuleUpdateResult:
    samples: int
    zero_mae: float
    update_mae: float
    shuffled_mae: float

    @property
    def improvement(self) -> float:
        return self.zero_mae - self.update_mae

    @property
    def beats_zero(self) -> bool:
        return self.update_mae < self.zero_mae

    @property
    def beats_shuffled(self) -> bool:
        return self.update_mae < self.shuffled_mae


class RuleUpdatePredictor:
    def __init__(self, ridge: float = 1e-6) -> None:
        if ridge < 0:
            raise ValueError("ridge must be >= 0")
        self.ridge = ridge

    def fit_predict(self, train, test) -> RuleUpdateResult:
        if not train or not test:
            return RuleUpdateResult(0, 0.0, 0.0, 0.0)
        x = np.asarray([row[0] for row in train], float)
        y = np.asarray([row[1] for row in train], float)
        v = np.asarray([row[0] for row in test], float)
        actual = np.asarray([row[1] for row in test], float)
        mean, scale = x.mean(0), x.std(0)
        scale[scale == 0] = 1.0
        xn, vn = (x - mean) / scale, (v - mean) / scale
        design = np.column_stack((np.ones(len(xn)), xn))
        reg = np.eye(design.shape[1])
        reg[0, 0] = 0.0
        coef = np.linalg.solve(design.T @ design + self.ridge * reg, design.T @ y)
        pred = np.column_stack((np.ones(len(vn)), vn)) @ coef
        shuffled = vn.copy()
        np.random.default_rng(390001).shuffle(shuffled)
        shuffled_pred = np.column_stack((np.ones(len(shuffled)), shuffled)) @ coef
        return RuleUpdateResult(
            len(actual),
            float(np.mean(np.abs(actual))),
            float(np.mean(np.abs(actual - pred))),
            float(np.mean(np.abs(actual - shuffled_pred))),
        )
