from __future__ import annotations

import numpy as np

from pw001_coupling_noise_ablation import evaluate


def bootstrap_mean(values: np.ndarray, rng: np.random.Generator, draws: int = 5000):
    samples = rng.choice(values, size=(draws, len(values)), replace=True)
    means = samples.mean(axis=1)
    return float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))


def collect(noise: float, actual: float, step: float, replicates: int = 20):
    values = []
    for replicate in range(replicates):
        seed = (
            397000
            + int(noise * 1_000_000) * 1000
            + int(actual * 100_000) * 10
            + int(step * 1_000_000_000)
            + replicate
        )
        candidates = tuple(
            sorted(
                {
                    max(0.0, actual - step),
                    actual,
                    actual + step,
                }
            )
        )
        results = evaluate(
            seed=seed,
            actual_coupling=actual,
            noise=noise,
            candidates=candidates,
        )
        best, _ = min(results, key=lambda item: item[1])
        values.append(best - actual)
    return np.asarray(values, dtype=float)


def main() -> None:
    rng = np.random.default_rng(255000)
    steps = (0.00025, 0.000125, 0.0000625, 0.00003125)
    actual_values = (0.0025, 0.01, 0.02)
    noise_values = (0.0, 0.001, 0.002)

    print("GENESIS-2.55 grid-resolution scaling control")
    print(
        "step noise actual mean_offset ci95_low ci95_high "
        "mean_abs_offset normalized_abs_offset n"
    )

    for step in steps:
        for noise in noise_values:
            for actual in actual_values:
                values = collect(noise, actual, step)
                low, high = bootstrap_mean(values, rng)
                mean_abs = float(np.abs(values).mean())
                normalized = mean_abs / step if step else 0.0
                print(
                    f"{step:.8g} {noise:.6g} {actual:.6g} "
                    f"{values.mean():.9g} {low:.9g} {high:.9g} "
                    f"{mean_abs:.9g} {normalized:.9g} {len(values)}"
                )


if __name__ == "__main__":
    main()
