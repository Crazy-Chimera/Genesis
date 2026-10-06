from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from genesis.core import GenesisConfig, GenesisUniverse


@dataclass(frozen=True)
class Result:
    actual: float
    candidate: float
    mae: float


def predicted_coherence(universe: GenesisUniverse, coupling: float) -> float:
    p = universe.phase
    local = (
        np.sin(np.roll(p, 1, 0) - p)
        + np.sin(np.roll(p, -1, 0) - p)
        + np.sin(np.roll(p, 1, 1) - p)
        + np.sin(np.roll(p, -1, 1) - p)
    ) / 4.0
    rng = np.random.default_rng(universe.config.seed + universe.tick)
    noise = rng.normal(0.0, universe.config.noise, p.shape)
    predicted = np.mod(
        p
        + universe.config.dt
        * (universe.omega + coupling * local + noise),
        2.0 * np.pi,
    )
    return float(abs(np.mean(np.exp(1j * predicted))))


def candidate_grid(actual: float) -> tuple[float, ...]:
    if actual == 0.0:
        values = np.arange(0.0, 0.0010001, 0.000125)
    else:
        values = np.arange(actual - 0.001, actual + 0.0010001, 0.000125)
    return tuple(float(max(0.0, value)) for value in values)


def evaluate(seed: int, actual: float, ticks: int = 2_000) -> tuple[Result, ...]:
    universe = GenesisUniverse(
        GenesisConfig(seed=seed, coupling=actual, ticks=ticks)
    )
    previous = float(abs(np.mean(np.exp(1j * universe.phase))))
    candidates = candidate_grid(actual)
    errors = {candidate: [] for candidate in candidates}

    for _ in range(ticks):
        predictions = {
            candidate: predicted_coherence(universe, candidate) - previous
            for candidate in candidates
        }
        universe.step()
        current = float(abs(np.mean(np.exp(1j * universe.phase))))
        target = current - previous
        for candidate in candidates:
            errors[candidate].append(abs(target - predictions[candidate]))
        previous = current

    return tuple(
        Result(actual, candidate, float(np.mean(errors[candidate])))
        for candidate in candidates
    )


def main() -> None:
    actual_values = (0.0, 0.0025, 0.005, 0.01, 0.015, 0.02)
    print("GENESIS-2.49 noise-aware fine coupling resolution")
    print("seed actual candidate mae")
    for offset, actual in enumerate(actual_values):
        seed = 390085 + offset
        results = evaluate(seed, actual)
        best = min(results, key=lambda result: result.mae)
        for result in results:
            print(
                seed,
                f"{result.actual:.9g}",
                f"{result.candidate:.9g}",
                f"{result.mae:.15g}",
            )
        print(
            "BEST",
            seed,
            f"{best.actual:.9g}",
            f"{best.candidate:.9g}",
            f"{best.mae:.15g}",
            "MATCH",
            best.candidate == best.actual,
        )


if __name__ == "__main__":
    main()
