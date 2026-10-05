from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from .core import GenesisConfig, GenesisUniverse


def deterministic_step(
    phase: np.ndarray,
    omega: np.ndarray,
    coupling_strength: float,
    dt: float,
) -> np.ndarray:
    """Apply one deterministic PW-001 update to a supplied phase field."""
    coupling = (
        np.sin(np.roll(phase, 1, 0) - phase)
        + np.sin(np.roll(phase, -1, 0) - phase)
        + np.sin(np.roll(phase, 1, 1) - phase)
        + np.sin(np.roll(phase, -1, 1) - phase)
    ) / 4.0
    return np.mod(
        phase + dt * (omega + coupling_strength * coupling),
        2.0 * np.pi,
    )


def coherence(phase: np.ndarray) -> float:
    return float(abs(np.mean(np.exp(1j * phase))))


def circular_rms(a: np.ndarray, b: np.ndarray) -> float:
    delta = np.angle(np.exp(1j * (a - b)))
    return float(np.sqrt(np.mean(delta * delta)))


@dataclass(frozen=True)
class ConvergenceResult:
    seed: int
    dt: float
    phase_rms: float
    coherence_error: float


def evaluate(seed: int, dt: float = 0.01) -> ConvergenceResult:
    if dt <= 0.0:
        raise ValueError("dt must be > 0")

    universe = GenesisUniverse(
        GenesisConfig(seed=seed, dt=dt, noise=0.0, ticks=1)
    )
    phase = universe.phase.copy()
    full = deterministic_step(
        phase, universe.omega, universe.config.coupling, dt
    )
    half = deterministic_step(
        phase, universe.omega, universe.config.coupling, dt / 2.0
    )
    half = deterministic_step(
        half, universe.omega, universe.config.coupling, dt / 2.0
    )

    return ConvergenceResult(
        seed=seed,
        dt=dt,
        phase_rms=circular_rms(full, half),
        coherence_error=abs(coherence(full) - coherence(half)),
    )
