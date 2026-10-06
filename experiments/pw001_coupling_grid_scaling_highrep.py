from __future__ import annotations

import numpy as np

from pw001_coupling_grid_scaling import bootstrap_mean, collect

STEPS = (0.00025, 0.000125, 0.0000625, 0.00003125)
NOISES = (0.001, 0.002)
ACTUAL = 0.01
REPLICATES = 200


def bootstrap_slope(
    steps: np.ndarray,
    abs_offsets: np.ndarray,
    rng: np.random.Generator,
    draws: int = 5000,
) -> tuple[float, float, float]:
    log_steps = np.log(steps)
    indices = rng.integers(0, len(steps), size=(draws, len(steps)))
    slopes = []
    for row in indices:
        slopes.append(np.polyfit(log_steps[row], np.log(abs_offsets[row]), 1)[0])
    slopes = np.asarray(slopes)
    return (
        float(np.quantile(slopes, 0.025)),
        float(np.median(slopes)),
        float(np.quantile(slopes, 0.975)),
    )


def main() -> None:
    rng = np.random.default_rng(257000)
    print("GENESIS-2.57 high-replication grid-scaling control")
    print("step noise actual mean_offset ci95_low ci95_high mean_abs_offset normalized_abs_offset n")

    for noise in NOISES:
        abs_values = []
        for step in STEPS:
            values = collect(noise, ACTUAL, step, replicates=REPLICATES)
            low, high = bootstrap_mean(values, rng)
            mean_abs = float(np.abs(values).mean())
            normalized = mean_abs / step
            abs_values.append(mean_abs)
            print(
                f"{step:.8g} {noise:.6g} {ACTUAL:.6g} "
                f"{values.mean():.9g} {low:.9g} {high:.9g} "
                f"{mean_abs:.9g} {normalized:.9g} {len(values)}"
            )

        slope_low, slope_mid, slope_high = bootstrap_slope(
            np.asarray(STEPS, dtype=float),
            np.asarray(abs_values, dtype=float),
            rng,
        )
        print(
            f"SLOPE {noise:.6g} alpha_ci95 "
            f"{slope_low:.6g} {slope_mid:.6g} {slope_high:.6g}"
        )


if __name__ == "__main__":
    main()
