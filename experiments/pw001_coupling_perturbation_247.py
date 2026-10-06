from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from genesis.core import GenesisConfig, GenesisUniverse


@dataclass(frozen=True)
class CouplingPerturbationResult:
    seed: int
    actual_coupling: float
    best_coupling: float
    best_mae: float
    zero_mae: float
    matched: bool


def predicted_innovation(universe: GenesisUniverse, coupling: float, previous: float) -> float:
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
    coherence = float(abs(np.mean(np.exp(1j * predicted))))
    return coherence - previous


def evaluate(
    seed: int,
    actual_coupling: float,
    candidates: tuple[float, ...],
    ticks: int = 2_000,
) -> CouplingPerturbationResult:
    universe = GenesisUniverse(
        GenesisConfig(seed=seed, coupling=actual_coupling, ticks=ticks)
    )
    previous = float(abs(np.mean(np.exp(1j * universe.phase))))
    errors = {candidate: [] for candidate in candidates}

    for _ in range(ticks):
        predictions = {
            candidate: predicted_innovation(universe, candidate, previous)
            for candidate in candidates
        }
        universe.step()
        actual = float(abs(np.mean(np.exp(1j * universe.phase))))
        target = actual - previous

        for candidate in candidates:
            errors[candidate].append(abs(target - predictions[candidate]))
        previous = actual

    maes = {candidate: float(np.mean(values)) for candidate, values in errors.items()}
    best = min(maes, key=maes.get)
    return CouplingPerturbationResult(
        seed=seed,
        actual_coupling=actual_coupling,
        best_coupling=best,
        best_mae=maes[best],
        zero_mae=maes[0.0],
        matched=np.isclose(best, actual_coupling),
    )


def main() -> None:
    actual_values = (0.0, 0.0025, 0.005, 0.01, 0.015, 0.02)
    candidates = actual_values
    print("GENESIS-2.47 controlled coupling perturbation")
    print("seed actual_coupling best_coupling best_mae zero_mae matched")

    matched = 0
    total = 0
    for offset, actual in enumerate(actual_values):
        seed = 390073 + offset
        result = evaluate(seed, actual, candidates)
        matched += int(result.matched)
        total += 1
        print(
            result.seed,
            f"{result.actual_coupling:.6g}",
            f"{result.best_coupling:.6g}",
            f"{result.best_mae:.15g}",
            f"{result.zero_mae:.15g}",
            result.matched,
        )

    print(f"MATCHED {matched}/{total}")


if __name__ == "__main__":
    main()
