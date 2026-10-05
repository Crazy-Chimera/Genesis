from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from .core import GenesisUniverse
from .mechanistic import rule_next_phase_without_noise


def rule_next_phase_frequency_only(universe: GenesisUniverse) -> np.ndarray:
    """Apply the intrinsic-frequency part of the update while removing coupling."""
    return np.mod(
        universe.phase + universe.config.dt * universe.omega,
        2.0 * np.pi,
    )


@dataclass(frozen=True)
class MechanisticDecompositionResult:
    samples: int
    zero_mae: float
    frequency_only_mae: float
    full_rule_mae: float

    @property
    def full_vs_frequency_improvement(self) -> float:
        return self.frequency_only_mae - self.full_rule_mae

    @property
    def full_beats_frequency_only(self) -> bool:
        return self.full_rule_mae < self.frequency_only_mae


class MechanisticDecompositionEvaluator:
    """Separate intrinsic-frequency and local-coupling predictive contributions."""

    @staticmethod
    def _coherence(phase: np.ndarray) -> float:
        return float(abs(np.mean(np.exp(1j * phase))))

    def evaluate(self, universe: GenesisUniverse) -> MechanisticDecompositionResult:
        previous = self._coherence(universe.phase)
        zero_errors: list[float] = []
        frequency_errors: list[float] = []
        full_errors: list[float] = []

        for _ in range(universe.config.ticks):
            frequency_phase = rule_next_phase_frequency_only(universe)
            full_phase = rule_next_phase_without_noise(universe)

            frequency_prediction = self._coherence(frequency_phase) - previous
            full_prediction = self._coherence(full_phase) - previous

            universe.step()
            actual = self._coherence(universe.phase)
            target = actual - previous

            zero_errors.append(abs(target))
            frequency_errors.append(abs(target - frequency_prediction))
            full_errors.append(abs(target - full_prediction))
            previous = actual

        if not zero_errors:
            return MechanisticDecompositionResult(0, 0.0, 0.0, 0.0)

        return MechanisticDecompositionResult(
            len(zero_errors),
            float(np.mean(zero_errors)),
            float(np.mean(frequency_errors)),
            float(np.mean(full_errors)),
        )
