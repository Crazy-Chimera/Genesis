from __future__ import annotations

from dataclasses import dataclass
import numpy as np


def rule_native_features(phase: np.ndarray, omega: np.ndarray) -> tuple[float, ...]:
    """Return coherence-free observables derived directly from the PW-001 local rule."""
    p = np.asarray(phase, dtype=float)
    w = np.asarray(omega, dtype=float)
    deltas = (
        np.roll(p, 1, 0) - p,
        np.roll(p, -1, 0) - p,
        np.roll(p, 1, 1) - p,
        np.roll(p, -1, 1) - p,
    )
    coupling = sum(np.sin(deltas)) / 4.0
    alignment = sum(np.cos(deltas)) / 4.0
    centered_w = w - float(np.mean(w))
    return (
        float(np.mean(coupling)),
        float(np.std(coupling)),
        float(np.mean(np.abs(coupling))),
        float(np.mean(coupling * coupling)),
        float(np.mean(alignment)),
        float(np.std(alignment)),
        float(np.mean(np.abs(alignment))),
        float(np.mean(centered_w)),
        float(np.std(centered_w)),
        float(np.mean(centered_w * centered_w)),
        float(np.mean(coupling * centered_w)),
        float(np.std(coupling * centered_w)),
    )


@dataclass(frozen=True)
class RuleNativeResult:
    samples: int
    zero_mae: float
    rule_mae: float
    shuffled_mae: float

    @property
    def improvement(self) -> float:
        return self.zero_mae - self.rule_mae

    @property
    def beats_zero(self) -> bool:
        return self.rule_mae < self.zero_mae

    @property
    def beats_shuffled(self) -> bool:
        return self.rule_mae < self.shuffled_mae


class RuleNativePredictor:
    """Predict next coherence innovation from coherence-free rule observables."""

    def __init__(self, ridge: float = 1e-6) -> None:
        if ridge < 0:
            raise ValueError("ridge must be >= 0")
        self.ridge = ridge

    def fit_predict(
        self,
        train: list[tuple[tuple[float, ...], float]],
        test: list[tuple[tuple[float, ...], float]],
    ) -> RuleNativeResult:
        if not train or not test:
            return RuleNativeResult(0, 0.0, 0.0, 0.0)
        x = np.asarray([r[0] for r in train], dtype=float)
        y = np.asarray([r[1] for r in train], dtype=float)
        v = np.asarray([r[0] for r in test], dtype=float)
        actual = np.asarray([r[1] for r in test], dtype=float)
        mean, scale = x.mean(0), x.std(0)
        scale[scale == 0] = 1.0
        xn = (x - mean) / scale
        vn = (v - mean) / scale
        design = np.column_stack((np.ones(len(xn)), xn))
        reg = np.eye(design.shape[1])
        reg[0, 0] = 0.0
        coef = np.linalg.solve(
            design.T @ design + self.ridge * reg,
            design.T @ y,
        )
        pred = np.column_stack((np.ones(len(vn)), vn)) @ coef
        shuffled = vn.copy()
        np.random.default_rng(390001).shuffle(shuffled)
        shuffled_pred = np.column_stack((np.ones(len(shuffled)), shuffled)) @ coef
        return RuleNativeResult(
            len(actual),
            float(np.mean(np.abs(actual))),
            float(np.mean(np.abs(actual - pred))),
            float(np.mean(np.abs(actual - shuffled_pred))),
        )
