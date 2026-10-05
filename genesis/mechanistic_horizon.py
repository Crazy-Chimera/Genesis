from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from .core import GenesisUniverse


def deterministic_next_phase(universe: GenesisUniverse, phase: np.ndarray) -> np.ndarray:
    """Compute one PW-001 update from a supplied phase, excluding deterministic noise."""
    coupling = (
        np.sin(np.roll(phase, 1, 0) - phase)
        + np.sin(np.roll(phase, -1, 0) - phase)
        + np.sin(np.roll(phase, 1, 1) - phase)
        + np.sin(np.roll(phase, -1, 1) - phase)
    ) / 4.0
    return np.mod(
        phase
        + universe.config.dt
        * (universe.omega + universe.config.coupling * coupling),
        2.0 * np.pi,
    )


def coherence(phase: np.ndarray) -> float:
    return float(abs(np.mean(np.exp(1j * phase))))


@dataclass(frozen=True)
class MechanisticHorizonResult:
    horizon: int
    samples: int
    zero_mae: float
    mechanistic_mae: float

    @property
    def improvement(self) -> float:
        return self.zero_mae - self.mechanistic_mae

    @property
    def beats_zero(self) -> bool:
        return self.mechanistic_mae < self.zero_mae


def evaluate_horizon(
    universe: GenesisUniverse,
    horizon: int,
) -> MechanisticHorizonResult:
    if horizon < 1:
        raise ValueError("horizon must be >= 1")

    previous = coherence(universe.phase)
    zero_errors: list[float] = []
    model_errors: list[float] = []

    for _ in range(universe.config.ticks):
        predicted = universe.phase.copy()
        for _ in range(horizon):
            predicted = deterministic_next_phase(universe, predicted)

        predicted_delta = coherence(predicted) - previous

        actual_phase = universe.phase.copy()
        for _ in range(horizon):
            universe.step()
            actual_phase = universe.phase.copy()

        actual_delta = coherence(actual_phase) - previous
        zero_errors.append(abs(actual_delta))
        model_errors.append(abs(actual_delta - predicted_delta))
        previous = coherence(actual_phase)

    return MechanisticHorizonResult(
        horizon=horizon,
        samples=len(zero_errors),
        zero_mae=float(np.mean(zero_errors)),
        mechanistic_mae=float(np.mean(model_errors)),
    )
