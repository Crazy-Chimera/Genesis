from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from .core import GenesisUniverse


def rule_next_phase_without_noise(universe: GenesisUniverse) -> np.ndarray:
    """Apply the PW-001 update equation while omitting the stochastic noise term."""
    p = universe.phase
    coupling = (
        np.sin(np.roll(p, 1, 0) - p)
        + np.sin(np.roll(p, -1, 0) - p)
        + np.sin(np.roll(p, 1, 1) - p)
        + np.sin(np.roll(p, -1, 1) - p)
    ) / 4.0
    return np.mod(
        p + universe.config.dt * (
            universe.omega + universe.config.coupling * coupling
        ),
        2.0 * np.pi,
    )


@dataclass(frozen=True)
class MechanisticResult:
    samples: int
    zero_mae: float
    mechanistic_mae: float

    @property
    def improvement(self) -> float:
        return self.zero_mae - self.mechanistic_mae

    @property
    def beats_zero(self) -> bool:
        return self.mechanistic_mae < self.zero_mae


class MechanisticOneStepPredictor:
    """Predict next coherence innovation from the explicit PW-001 rule."""

    def evaluate(self, universe: GenesisUniverse) -> MechanisticResult:
        previous = float(abs(np.mean(np.exp(1j * universe.phase))))
        zero_errors: list[float] = []
        model_errors: list[float] = []

        for _ in range(universe.config.ticks):
            predicted_phase = rule_next_phase_without_noise(universe)
            predicted_coherence = float(abs(np.mean(np.exp(1j * predicted_phase))))
            universe.step()
            actual_coherence = float(abs(np.mean(np.exp(1j * universe.phase))))
            target = actual_coherence - previous
            prediction = predicted_coherence - previous
            zero_errors.append(abs(target))
            model_errors.append(abs(target - prediction))
            previous = actual_coherence

        if not zero_errors:
            return MechanisticResult(0, 0.0, 0.0)
        return MechanisticResult(
            len(zero_errors),
            float(np.mean(zero_errors)),
            float(np.mean(model_errors)),
        )
