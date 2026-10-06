from __future__ import annotations

import numpy as np

try:
    from experiments.pw001_coupling_noise_ablation import evaluate
except ModuleNotFoundError:
    from pw001_coupling_noise_ablation import evaluate


def main() -> None:
    actual_values = (0.0025, 0.01, 0.02)
    noise_values = (0.0, 0.00025, 0.0005, 0.001, 0.002)
    offset = 0.000125
    replicates = 30

    print("GENESIS-2.52 statistical coupling/noise offset replication")
    print("noise actual_coupling exact_rate mean_abs_offset mean_offset "
          "negative_rate positive_rate n")

    for noise_index, noise in enumerate(noise_values):
        for actual_index, actual in enumerate(actual_values):
            offsets: list[float] = []
            for replicate in range(replicates):
                seed = 394000 + noise_index * 1000 + actual_index * 100 + replicate
                candidates = tuple(sorted({
                    max(0.0, actual - offset), actual, actual + offset
                }))
                results = evaluate(
                    seed=seed,
                    actual_coupling=actual,
                    noise=noise,
                    candidates=candidates,
                )
                best_coupling, _ = min(results, key=lambda item: item[1])
                offsets.append(best_coupling - actual)

            values = np.asarray(offsets, dtype=float)
            exact_rate = float(np.mean(np.isclose(values, 0.0, atol=1e-15)))
            mean_abs = float(np.mean(np.abs(values)))
            mean_offset = float(np.mean(values))
            negative_rate = float(np.mean(values < 0.0))
            positive_rate = float(np.mean(values > 0.0))
            print(
                f"{noise:.6g} {actual:.6g} {exact_rate:.6f} "
                f"{mean_abs:.9g} {mean_offset:.9g} "
                f"{negative_rate:.6f} {positive_rate:.6f} {len(values)}"
            )


if __name__ == "__main__":
    main()
