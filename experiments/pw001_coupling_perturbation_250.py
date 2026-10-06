from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from genesis.core import GenesisConfig, GenesisUniverse


@dataclass(frozen=True)
class Result:
    seed: int
    actual: float
    best: float
    best_mae: float
    zero_mae: float
    match: bool


def predicted_innovation(
    universe: GenesisUniverse, coupling: float, previous: float
) -> float:
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


def grid(actual: float) -> tuple[float, ...]:
    if actual == 0.0:
        values = np.arange(0.0, 0.0010001, 0.000125)
    else:
        values = np.arange(actual - 0.001, actual + 0.0010001, 0.000125)
    return tuple(float(max(0.0, value)) for value in values)


def evaluate(seed: int, actual: float, ticks: int = 2_000) -> Result:
    universe = GenesisUniverse(
        GenesisConfig(seed=seed, coupling=actual, ticks=ticks)
    )
    previous = float(abs(np.mean(np.exp(1j * universe.phase))))
    candidates = grid(actual)
    errors = {candidate: [] for candidate in candidates}

    for _ in range(ticks):
        predictions = {
            candidate: predicted_innovation(universe, candidate, previous)
            for candidate in candidates
        }
        universe.step()
        current = float(abs(np.mean(np.exp(1j * universe.phase))))
        target = current - previous
        for candidate in candidates:
            errors[candidate].append(abs(target - predictions[candidate]))
        previous = current

    maes = {candidate: float(np.mean(values)) for candidate, values in errors.items()}
    best = min(maes, key=maes.get)
    return Result(
        seed=seed,
        actual=actual,
        best=best,
        best_mae=maes[best],
        zero_mae=maes.get(0.0, float("nan")),
        match=bool(np.isclose(best, actual)),
    )


def main() -> None:
    actual_values = (0.0, 0.0025, 0.005, 0.01, 0.015, 0.02)
    print("GENESIS-2.50 noise-blind fine coupling replication")
    print("seed actual best best_mae zero_mae match")
    results = []
    for offset, actual in enumerate(actual_values):
        result = evaluate(390091 + offset, actual)
        results.append(result)
        print(
            result.seed,
            f"{result.actual:.9g}",
            f"{result.best:.9g}",
            f"{result.best_mae:.15g}",
            f"{result.zero_mae:.15g}",
            result.match,
        )
    print(
        "MATCHED",
        sum(result.match for result in results),
        f"/{len(results)}",
    )


if __name__ == "__main__":
    main()
