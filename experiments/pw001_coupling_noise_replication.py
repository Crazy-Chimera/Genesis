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

    print("GENESIS-2.51 unseen-seed coupling/noise replication")
    print("noise seed actual_coupling best_coupling best_mae exact_match offset")

    for noise_index, noise in enumerate(noise_values):
        for replicate in range(3):
            for coupling_index, actual in enumerate(actual_values):
                seed = 393000 + noise_index * 100 + replicate * 10 + coupling_index
                candidates = tuple(sorted({
                    max(0.0, actual - offset), actual, actual + offset
                }))
                results = evaluate(
                    seed=seed,
                    actual_coupling=actual,
                    noise=noise,
                    candidates=candidates,
                )
                best_coupling, best_mae = min(results, key=lambda item: item[1])
                signed_offset = best_coupling - actual
                exact = bool(np.isclose(best_coupling, actual, atol=1e-15))
                print(
                    f"{noise:.6g} {seed} {actual:.6g} "
                    f"{best_coupling:.9g} {best_mae:.15g} "
                    f"{exact} {signed_offset:.9g}"
                )


if __name__ == "__main__":
    main()
