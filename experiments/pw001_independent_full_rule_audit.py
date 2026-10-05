from __future__ import annotations

import numpy as np

from genesis.core import GenesisConfig, GenesisUniverse


def independent_step(
    phase: np.ndarray,
    omega: np.ndarray,
    *,
    coupling: float,
    dt: float,
    noise_scale: float,
    noise_seed: int,
) -> np.ndarray:
    """Independent explicit-index reproduction of the complete PW-001 update."""
    size = phase.shape[0]
    rng = np.random.default_rng(noise_seed)
    noise = rng.normal(0.0, noise_scale, phase.shape)
    out = np.empty_like(phase)

    for row in range(size):
        for col in range(size):
            p = phase[row, col]
            neighbors = (
                phase[(row - 1) % size, col],
                phase[(row + 1) % size, col],
                phase[row, (col - 1) % size],
                phase[row, (col + 1) % size],
            )
            local = sum(np.sin(q - p) for q in neighbors) / 4.0
            out[row, col] = np.mod(
                p + dt * (
                    omega[row, col]
                    + coupling * local
                    + noise[row, col]
                ),
                2.0 * np.pi,
            )
    return out


def coherence(phase: np.ndarray) -> float:
    return float(abs(np.mean(np.exp(1j * phase))))


def circular_error(expected: np.ndarray, actual: np.ndarray) -> float:
    delta = np.angle(np.exp(1j * (expected - actual)))
    return float(np.max(np.abs(delta)))


def evaluate(seed: int, ticks: int = 2_000) -> tuple[float, float]:
    config = GenesisConfig(seed=seed, ticks=ticks)
    universe = GenesisUniverse(config)
    max_phase_error = 0.0
    max_coherence_error = 0.0

    for _ in range(ticks):
        before = universe.phase.copy()
        expected = independent_step(
            before,
            universe.omega,
            coupling=config.coupling,
            dt=config.dt,
            noise_scale=config.noise,
            noise_seed=config.seed + universe.tick,
        )
        universe.step()

        max_phase_error = max(
            max_phase_error,
            circular_error(expected, universe.phase),
        )
        max_coherence_error = max(
            max_coherence_error,
            abs(coherence(expected) - coherence(universe.phase)),
        )

    return max_phase_error, max_coherence_error


def main() -> None:
    print("GENESIS-2.42 independent full-rule implementation audit")
    print("seed max_circular_phase_error max_coherence_error")
    for seed in range(390049, 390055):
        phase_error, coherence_error = evaluate(seed)
        print(
            seed,
            f"{phase_error:.15g}",
            f"{coherence_error:.15g}",
        )


if __name__ == "__main__":
    main()
