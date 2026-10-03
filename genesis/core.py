from __future__ import annotations

from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class GenesisConfig:
    """Parameters that define the GENESIS-PW-001 universe."""

    size: int = 16
    coupling: float = 0.01
    frequency_mean: float = 1.0
    frequency_std: float = 0.05
    noise: float = 0.001
    dt: float = 0.01
    seed: int = 390001
    ticks: int = 100_000

    @property
    def count(self) -> int:
        return self.size * self.size


class GenesisUniverse:
    """The universe rules. It contains no entity or intelligence semantics."""

    def __init__(self, config: GenesisConfig = GenesisConfig()) -> None:
        self.config = config
        rng = np.random.default_rng(config.seed)

        shape = (config.size, config.size)
        self.phase = rng.uniform(0.0, 2.0 * np.pi, shape)
        self.omega = rng.normal(
            config.frequency_mean, config.frequency_std, shape
        )
        self.amplitude = np.ones(shape, dtype=np.float64)
        self.tick = 0

    def step(self) -> np.ndarray:
        """Advance one local-interaction step and return the new phase field."""
        p = self.phase

        # Four-neighbour periodic topology: locality is part of the universe rule.
        coupling = (
            np.sin(np.roll(p, 1, 0) - p)
            + np.sin(np.roll(p, -1, 0) - p)
            + np.sin(np.roll(p, 1, 1) - p)
            + np.sin(np.roll(p, -1, 1) - p)
        ) / 4.0

        rng = np.random.default_rng(self.config.seed + self.tick)
        noise = rng.normal(0.0, self.config.noise, p.shape)

        self.phase = np.mod(
            p + self.config.dt * (self.omega + self.config.coupling * coupling + noise),
            2.0 * np.pi,
        )
        self.tick += 1
        return self.phase

    def state(self) -> dict[str, np.ndarray | int]:
        return {
            "phase": self.phase.copy(),
            "omega": self.omega.copy(),
            "amplitude": self.amplitude.copy(),
            "tick": self.tick,
        }


class GenesisObserver:
    """External measurement layer; it does not modify universe rules."""

    @staticmethod
    def coherence(phase: np.ndarray) -> float:
        z = np.mean(np.exp(1j * phase))
        return float(np.abs(z))

    def measure(self, universe: GenesisUniverse) -> dict[str, float | int]:
        return {
            "tick": universe.tick,
            "coherence": self.coherence(universe.phase),
        }


def run(config: GenesisConfig = GenesisConfig()) -> list[dict[str, float | int]]:
    universe = GenesisUniverse(config)
    observer = GenesisObserver()
    measurements = [observer.measure(universe)]

    for _ in range(config.ticks):
        universe.step()
        measurements.append(observer.measure(universe))

    return measurements
