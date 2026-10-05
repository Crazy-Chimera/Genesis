from __future__ import annotations

import numpy as np

from genesis.core import GenesisConfig, GenesisUniverse
from genesis.rule_transition import rule_transition_features


SOURCE_SEEDS = tuple(range(390013, 390025))
TARGET_SEEDS = tuple(range(390025, 390037))
TICKS = 600
TRAIN_END = 300
GAP_END = 450
PERMUTATIONS = 500


def collect(seed: int):
    universe = GenesisUniverse(GenesisConfig(seed=seed, ticks=TICKS))
    rows = []
    previous_phase = universe.phase.copy()
    previous_coherence = float(abs(np.mean(np.exp(1j * previous_phase))))

    for _ in range(TICKS):
        universe.step()
        phase = universe.phase
        coherence = float(abs(np.mean(np.exp(1j * phase))))
        features = rule_transition_features(
            previous_phase, phase, universe.omega, universe.config.coupling
        )
        rows.append((features, coherence - previous_coherence))
        previous_phase = phase.copy()
        previous_coherence = coherence
    return rows


def fit(train):
    x = np.asarray([row[0] for row in train], dtype=np.float64)
    y = np.asarray([row[1] for row in train], dtype=np.float64)
    mean = x.mean(axis=0)
    scale = x.std(axis=0)
    scale[scale == 0.0] = 1.0
    xn = (x - mean) / scale
    design = np.column_stack((np.ones(len(xn)), xn))
    regularizer = np.eye(design.shape[1])
    regularizer[0, 0] = 0.0
    coef = np.linalg.solve(
        design.T @ design + 1e-6 * regularizer,
        design.T @ y,
    )
    return mean, scale, coef


def predict(features, model):
    mean, scale, coef = model
    x = np.asarray(features, dtype=np.float64)
    xn = (x - mean) / scale
    return np.column_stack((np.ones(len(xn)), xn)) @ coef


def main() -> None:
    source = {seed: collect(seed) for seed in SOURCE_SEEDS}
    target = {seed: collect(seed) for seed in TARGET_SEEDS}
    train = [row for seed in SOURCE_SEEDS for row in source[seed][:TRAIN_END]]
    model = fit(train)

    rng = np.random.default_rng(390032)
    case_pvalues = []

    print(
        "GENESIS-2.33 permutation audit; "
        f"source={SOURCE_SEEDS}; target={TARGET_SEEDS}; "
        f"train=0:{TRAIN_END}; gap={TRAIN_END}:{GAP_END}; "
        f"test={GAP_END}:{TICKS}; permutations={PERMUTATIONS}"
    )

    for seed in TARGET_SEEDS:
        test = target[seed][GAP_END:TICKS]
        features = np.asarray([row[0] for row in test], dtype=np.float64)
        actual = np.asarray([row[1] for row in test], dtype=np.float64)
        prediction = predict(features, model)
        observed_improvement = float(
            np.mean(np.abs(actual)) - np.mean(np.abs(actual - prediction))
        )

        null = np.empty(PERMUTATIONS, dtype=np.float64)
        for index in range(PERMUTATIONS):
            permutation = rng.permutation(len(features))
            shuffled_prediction = predict(features[permutation], model)
            null[index] = float(
                np.mean(np.abs(actual))
                - np.mean(np.abs(actual - shuffled_prediction))
            )

        p_value = float((1 + np.sum(null >= observed_improvement)) / (PERMUTATIONS + 1))
        case_pvalues.append(p_value)
        print(seed, len(test), f"{observed_improvement:.15g}", f"{p_value:.6g}")

    print("SUMMARY")
    print(f"cases={len(case_pvalues)}")
    print(f"p_lt_0_05={sum(p < 0.05 for p in case_pvalues)}")
    print(f"median_p={float(np.median(case_pvalues)):.6g}")
    print(f"min_p={min(case_pvalues):.6g}")


if __name__ == "__main__":
    main()
