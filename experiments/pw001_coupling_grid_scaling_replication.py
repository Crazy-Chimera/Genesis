from __future__ import annotations

import numpy as np

from pw001_coupling_grid_scaling import bootstrap_mean, collect

STEPS = (0.00025, 0.000125, 0.0000625, 0.00003125)
NOISES = (0.001, 0.002)
ACTUAL = 0.01
REPLICATES = 50


def main() -> None:
    rng = np.random.default_rng(256000)
    print("GENESIS-2.56 replicated grid-convergence control")
    print(
        "step noise actual mean_offset ci95_low ci95_high "
        "mean_abs_offset normalized_abs_offset n"
    )
    for step in STEPS:
        for noise in NOISES:
            values = collect(noise, ACTUAL, step, replicates=REPLICATES)
            low, high = bootstrap_mean(values, rng)
            mean_abs = float(np.abs(values).mean())
            normalized = mean_abs / step
            print(
                f"{step:.8g} {noise:.6g} {ACTUAL:.6g} "
                f"{values.mean():.9g} {low:.9g} {high:.9g} "
                f"{mean_abs:.9g} {normalized:.9g} {len(values)}"
            )


if __name__ == "__main__":
    main()
