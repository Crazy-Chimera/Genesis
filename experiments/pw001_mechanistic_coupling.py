from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from genesis.core import GenesisConfig, GenesisUniverse


@dataclass(frozen=True)
class CouplingSweepResult:
    coupling: float
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


def evaluate(seed: int, couplings: tuple[float, ...], ticks: int = 2_000):
    universe = GenesisUniverse(GenesisConfig(seed=seed, ticks=ticks))
    previous = float(abs(np.mean(np.exp(1j * universe.phase))))
    errors = {k: [] for k in couplings}

    for _ in range(ticks):
        predictions = {
            k: predicted_coherence(universe, k) - previous for k in couplings
        }
        universe.step()
        actual = float(abs(np.mean(np.exp(1j * universe.phase))))
        target = actual - previous
        for k in couplings:
            errors[k].append(abs(target - predictions[k]))
        previous = actual

    return tuple(
        CouplingSweepResult(k, float(np.mean(errors[k])))
        for k in couplings
    )


def main() -> None:
    couplings = (0.0, 0.0025, 0.005, 0.0075, 0.01, 0.0125, 0.015, 0.02)
    print("GENESIS-2.39 coupling dose-response validation")
    print("seed coupling mae")
    for seed in range(390037, 390043):
        results = evaluate(seed, couplings)
        best = min(results, key=lambda r: r.mae)
        for result in results:
            print(seed, f"{result.coupling:.6g}", f"{result.mae:.15g}")
        print("BEST", seed, f"{best.coupling:.6g}", f"{best.mae:.15g}")


if __name__ == "__main__":
    main()
