from __future__ import annotations

import numpy as np

from genesis.core import GenesisConfig, GenesisUniverse
from experiments.pw001_mechanistic_coupling import predicted_coherence


ACTUAL = 0.01
NOISES = (0.001, 0.002)
OFFSET = 0.001
STEP = 0.000125
REPLICATES = 50
TICKS = 2_000
BOOTSTRAP = 5_000


def candidates(actual: float) -> tuple[float, ...]:
    values = np.arange(
        actual - OFFSET,
        actual + OFFSET + STEP / 2,
        STEP,
        dtype=float,
    )
    return tuple(float(max(0.0, value)) for value in values)


def surface(seed: int, actual: float, noise: float) -> np.ndarray:
    universe = GenesisUniverse(
        GenesisConfig(seed=seed, coupling=actual, noise=noise, ticks=TICKS)
    )
    grid = candidates(actual)
    errors = np.zeros(len(grid), dtype=float)
    previous = float(abs(np.mean(np.exp(1j * universe.phase))))

    for _ in range(TICKS):
        predictions = np.asarray(
            [predicted_coherence(universe, coupling) - previous for coupling in grid]
        )
        universe.step()
        current = float(abs(np.mean(np.exp(1j * universe.phase))))
        target = current - previous
        errors += np.abs(target - predictions)
        previous = current

    return errors / TICKS


def bootstrap_confidence_set(
    surfaces: np.ndarray,
    grid: tuple[float, ...],
    rng: np.random.Generator,
) -> tuple[tuple[float, ...], tuple[float, float]]:
    best = int(np.argmin(surfaces.mean(axis=0)))
    differences = surfaces - surfaces[:, [best]]
    indices = rng.integers(0, len(surfaces), size=(BOOTSTRAP, len(surfaces)))
    boot = differences[indices].mean(axis=1)
    low = np.quantile(boot, 0.025, axis=0)
    high = np.quantile(boot, 0.975, axis=0)
    included = tuple(
        float(grid[i]) for i in range(len(grid))
        if low[i] <= 0.0 <= high[i]
    )
    return included, (float(grid[best]), float(np.min(surfaces.mean(axis=0))))


def classify(region: tuple[float, ...], actual: float) -> str:
    if region == (actual,):
        return "exact"
    if actual in region:
        return "interval"
    return "non-identifiable"


def main() -> None:
    rng = np.random.default_rng(257000)
    grid = candidates(ACTUAL)

    print("GENESIS-2.57 coupling-minimum confidence region")
    print(
        "noise replicates candidate_grid best_mean_coupling "
        "confidence_set classification"
    )

    for noise_index, noise in enumerate(NOISES):
        surfaces = np.vstack(
            [
                surface(
                    seed=396000 + noise_index * 1000 + replicate,
                    actual=ACTUAL,
                    noise=noise,
                )
                for replicate in range(REPLICATES)
            ]
        )
        region, (best, best_mae) = bootstrap_confidence_set(
            surfaces, grid, rng
        )
        print(
            f"{noise:.6g} {REPLICATES} "
            f"{','.join(f'{v:.9g}' for v in grid)} "
            f"{best:.9g} {best_mae:.15g} "
            f"{','.join(f'{v:.9g}' for v in region)} "
            f"{classify(region, ACTUAL)}"
        )


if __name__ == "__main__":
    main()
