from __future__ import annotations

import numpy as np

from experiments.pw001_coupling_noise_ablation import evaluate


def bootstrap_mean(values: np.ndarray, rng: np.random.Generator, draws: int = 5000):
    samples = rng.choice(values, size=(draws, len(values)), replace=True)
    means = samples.mean(axis=1)
    return float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))


def collect(noise: float, actual: float, replicates: int = 30):
    offset = 0.000125
    values = []
    for replicate in range(replicates):
        seed = 395000 + int(noise * 1_000_000) * 100 + int(actual * 100_000) + replicate
        candidates = tuple(sorted({
            max(0.0, actual - offset), actual, actual + offset
        }))
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
    rng = np.random.default_rng(253000)
    actual_values = (0.0025, 0.01, 0.02)
    noise_values = (0.0, 0.00025, 0.0005, 0.001, 0.002)

    print("GENESIS-2.53 bootstrap uncertainty of coupling offsets")
    print("noise actual mean_offset ci95_low ci95_high mean_abs_offset "
          "positive_rate negative_rate n")

    for noise in noise_values:
        for actual in actual_values:
            values = collect(noise, actual)
            low, high = bootstrap_mean(values, rng)
            print(
                f"{noise:.6g} {actual:.6g} "
                f"{values.mean():.9g} {low:.9g} {high:.9g} "
                f"{np.abs(values).mean():.9g} "
                f"{np.mean(values > 0):.6f} {np.mean(values < 0):.6f} "
                f"{len(values)}"
            )


if __name__ == "__main__":
    main()
