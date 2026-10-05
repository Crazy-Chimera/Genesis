from __future__ import annotations

from genesis.numerical_convergence import evaluate

SEEDS = tuple(range(390061, 390067))
DTS = (0.01, 0.005, 0.0025, 0.00125)


def main() -> None:
    print("GENESIS-2.45 numerical convergence audit")
    print("seed dt phase_rms coherence_error")
    for seed in SEEDS:
        for dt in DTS:
            result = evaluate(seed, dt)
            print(
                seed,
                f"{dt:.8g}",
                f"{result.phase_rms:.15g}",
                f"{result.coherence_error:.15g}",
            )


if __name__ == "__main__":
    main()
