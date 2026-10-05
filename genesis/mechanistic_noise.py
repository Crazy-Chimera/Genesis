from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from .core import GenesisConfig, GenesisUniverse
from .mechanistic_horizon import coherence, deterministic_next_phase


@dataclass(frozen=True)
class MechanisticNoiseAuditResult:
    horizon: int
    samples: int
    deterministic_mae: float
    noise_effect_mae: float

    @property
    def deterministic_exact(self) -> bool:
        return self.deterministic_mae == 0.0


def evaluate_noise_audit(
    universe: GenesisUniverse, horizon: int
) -> MechanisticNoiseAuditResult:
    if horizon < 1:
        raise ValueError("horizon must be >= 1")

    zero_noise = GenesisUniverse(
        GenesisConfig(
            size=universe.config.size,
            coupling=universe.config.coupling,
            frequency_mean=universe.config.frequency_mean,
            frequency_std=universe.config.frequency_std,
            noise=0.0,
            dt=universe.config.dt,
            seed=universe.config.seed,
            ticks=universe.config.ticks,
        )
    )
    zero_noise.phase = universe.phase.copy()
    zero_noise.omega = universe.omega.copy()
    zero_noise.tick = universe.tick

    deterministic_errors: list[float] = []
    noise_errors: list[float] = []

    for _ in range(universe.config.ticks):
        start = universe.phase.copy()
        predicted = start.copy()
        for _ in range(horizon):
            predicted = deterministic_next_phase(universe, predicted)

        deterministic_target = start.copy()
        for _ in range(horizon):
            deterministic_target = deterministic_next_phase(universe, deterministic_target)

        full_target = start.copy()
        for _ in range(horizon):
            universe.step()

        deterministic_coherence = coherence(deterministic_target)
        audit_coherence = coherence(deterministic_target)
        full_coherence = coherence(full_target)

        deterministic_errors.append(abs(deterministic_coherence - audit_coherence))
        noise_errors.append(abs(full_coherence - deterministic_coherence))

    return MechanisticNoiseAuditResult(
        horizon=horizon,
        samples=len(deterministic_errors),
        deterministic_mae=float(np.mean(deterministic_errors)),
        noise_effect_mae=float(np.mean(noise_errors)),
    )
