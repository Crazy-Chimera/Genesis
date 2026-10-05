from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from genesis.core import GenesisConfig, GenesisUniverse


@dataclass(frozen=True)
class AblationResult:
    actual_coupling: float
    candidate_coupling: float
    mae: float


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
    candidates: tuple[float, ...],
    ticks: int = 2_000,
) -> tuple[AblationResult, ...]:
    universe = GenesisUniverse(
        GenesisConfig(seed=seed, coupling=actual_coupling, ticks=ticks)
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
        AblationResult(actual_coupling, candidate, float(np.mean(errors[candidate])))
        for candidate in candidates
    )


def main() -> None:
    actual_values = (0.0, 0.005, 0.01, 0.015)
    candidates = (0.0, 0.0025, 0.005, 0.0075, 0.01, 0.0125, 0.015, 0.02)

    print("GENESIS-2.45 controlled coupling perturbation")
    print("seed actual_coupling candidate_coupling mae")
    for offset, actual in enumerate(actual_values):
        seed = 390061 + offset
        results = evaluate(seed, actual, candidates)
        best = min(results, key=lambda result: result.mae)
        for result in results:
            print(
                seed,
                f"{result.actual_coupling:.6g}",
                f"{result.candidate_coupling:.6g}",
                f"{result.mae:.15g}",
            )
        print(
            "BEST",
            seed,
            f"{best.actual_coupling:.6g}",
            f"{best.candidate_coupling:.6g}",
            f"{best.mae:.15g}",
        )


if __name__ == "__main__":
    main()
