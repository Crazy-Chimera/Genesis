from __future__ import annotations

import numpy as np

from genesis.core import GenesisConfig, GenesisUniverse


def predicted_coherence(universe: GenesisUniverse, coupling: float) -> float:
    p = universe.phase
    local = (
        np.sin(np.roll(p, 1, 0) - p)
        + np.sin(np.roll(p, -1, 0) - p)
        + np.sin(np.roll(p, 1, 1) - p)
        + np.sin(np.roll(p, -1, 1) - p)
    ) / 4.0
    predicted = np.mod(
        p + universe.config.dt * (universe.omega + coupling * local),
        2.0 * np.pi,
    )
    return float(abs(np.mean(np.exp(1j * predicted))))


def evaluate(
    seed: int,
    actual_coupling: float,
    noise: float,
    candidates: tuple[float, ...],
    ticks: int = 2_000,
) -> tuple[tuple[float, float], ...]:
    universe = GenesisUniverse(
        GenesisConfig(
            seed=seed,
            coupling=actual_coupling,
            noise=noise,
            ticks=ticks,
        )
    )
    previous = float(abs(np.mean(np.exp(1j * universe.phase))))
    errors = {candidate: [] for candidate in candidates}

    for _ in range(ticks):
        predictions = {
            candidate: predicted_coherence(universe, candidate) - previous
            for candidate in candidates
        }
        universe.step()
        actual = float(abs(np.mean(np.exp(1j * universe.phase))))
        target = actual - previous
        for candidate in candidates:
            errors[candidate].append(abs(target - predictions[candidate]))
        previous = actual

    return tuple(
        (candidate, float(np.mean(errors[candidate])))
        for candidate in candidates
    )


def main() -> None:
    actual_values = (0.0, 0.0025, 0.005, 0.01, 0.015, 0.02)
    offset = 0.000125
    for noise in (0.001, 0.0):
        print(f"GENESIS-2.49 coupling noise ablation noise={noise:g}")
        print("seed actual_coupling best_coupling best_mae exact_match")
        for index, actual in enumerate(actual_values):
            seed = 390079 + index
            candidates = tuple(
                sorted(
                    {
                        max(0.0, actual - offset),
                        actual,
                        actual + offset,
                    }
                )
            )
            results = evaluate(seed, actual, noise, candidates)
            best_coupling, best_mae = min(results, key=lambda item: item[1])
            exact = bool(np.isclose(best_coupling, actual, atol=1e-15))
            print(
                seed,
                f"{actual:.6g}",
                f"{best_coupling:.9g}",
                f"{best_mae:.15g}",
                exact,
            )


if __name__ == "__main__":
    main()
