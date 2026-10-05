from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from .core import GenesisUniverse


@dataclass(frozen=True)
class PrecisionAuditResult:
    horizon: int
    samples: int
    mean_coherence_gap: float
    max_coherence_gap: float
    mean_phase_gap: float
    max_phase_gap: float


def _next_phase(
    universe: GenesisUniverse,
    phase: np.ndarray,
    dtype: np.dtype,
) -> np.ndarray:
    p = np.asarray(phase, dtype=dtype)
    omega = np.asarray(universe.omega, dtype=dtype)
    coupling = (
        np.sin(np.roll(p, 1, 0) - p)
        + np.sin(np.roll(p, -1, 0) - p)
        + np.sin(np.roll(p, 1, 1) - p)
        + np.sin(np.roll(p, -1, 1) - p)
    ) / dtype.type(4.0)
    value = p + dtype.type(universe.config.dt) * (
        omega + dtype.type(universe.config.coupling) * coupling
    )
    return np.mod(value, dtype.type(2.0 * np.pi)).astype(dtype)


def _coherence(phase: np.ndarray) -> float:
    return float(abs(np.mean(np.exp(1j * phase.astype(np.float64)))))


def _circular_gap(a: np.ndarray, b: np.ndarray) -> float:
    delta = np.angle(np.exp(1j * (a.astype(np.float64) - b.astype(np.float64))))
    return float(np.max(np.abs(delta)))


def evaluate_precision_audit(
    universe: GenesisUniverse,
    horizon: int,
) -> PrecisionAuditResult:
    if horizon < 1:
        raise ValueError("horizon must be >= 1")

    coherence_gaps: list[float] = []
    phase_gaps: list[float] = []

    for _ in range(universe.config.ticks):
        start = universe.phase.copy()
        p64 = start.astype(np.float64)
        p32 = start.astype(np.float32)

        for _ in range(horizon):
            p64 = _next_phase(universe, p64, np.dtype(np.float64))
            p32 = _next_phase(universe, p32, np.dtype(np.float32))

        coherence_gaps.append(abs(_coherence(p64) - _coherence(p32)))
        phase_gaps.append(_circular_gap(p64, p32))
        universe.step()

    return PrecisionAuditResult(
        horizon=horizon,
        samples=len(coherence_gaps),
        mean_coherence_gap=float(np.mean(coherence_gaps)),
        max_coherence_gap=float(np.max(coherence_gaps)),
        mean_phase_gap=float(np.mean(phase_gaps)),
        max_phase_gap=float(np.max(phase_gaps)),
    )
