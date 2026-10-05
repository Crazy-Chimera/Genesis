from __future__ import annotations

import numpy as np

from genesis.core import GenesisConfig, GenesisUniverse


def independent_step_phase(
    phase: np.ndarray,
    omega: np.ndarray,
    coupling: float,
    dt: float,
) -> np.ndarray:
    """Independent explicit-index implementation of the PW-001 deterministic rule."""
    size = phase.shape[0]
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
                p + dt * (omega[row, col] + coupling * local),
                2.0 * np.pi,
            )
    return out


def coherence(phase: np.ndarray) -> float:
    return float(abs(np.mean(np.exp(1j * phase))))


def evaluate(seed: int, ticks: int = 2_000) -> tuple[float, float, float]:
    universe = GenesisUniverse(GenesisConfig(seed=seed, ticks=ticks))
    max_phase_error = 0.0
    max_coherence_error = 0.0
    prediction_errors: list[float] = []

    for _ in range(ticks):
        before = universe.phase.copy()
        expected = independent_step_phase(
            before,
            universe.omega,
            universe.config.coupling,
            universe.config.dt,
        )
        predicted_delta = coherence(expected) - coherence(before)
        universe.step()
        actual_delta = coherence(universe.phase) - coherence(before)

        max_phase_error = max(
            max_phase_error, float(np.max(np.abs(expected - universe.phase)))
        )
        max_coherence_error = max(
            max_coherence_error, abs(coherence(expected) - coherence(universe.phase))
        )
        prediction_errors.append(abs(actual_delta - predicted_delta))

    return (
        max_phase_error,
        max_coherence_error,
        float(np.mean(prediction_errors)),
    )


def main() -> None:
    print("GENESIS-2.41 independent mechanistic equation audit")
    print("seed max_phase_error max_coherence_error mean_prediction_mae")
    for seed in range(390049, 390055):
        phase_error, coherence_error, mae = evaluate(seed)
        print(
            seed,
            f"{phase_error:.15g}",
            f"{coherence_error:.15g}",
            f"{mae:.15g}",
        )


if __name__ == "__main__":
    main()
