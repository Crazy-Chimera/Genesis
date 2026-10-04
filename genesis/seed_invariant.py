from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np

from .cross_seed_generalization import _split
from .memory import MemoryRecord
from .state_innovation import combined_state


@dataclass(frozen=True)
class SeedInvariantResult:
    train_seeds: tuple[int, ...]
    target_seed: int
    history_length: int
    samples: int
    zero_mae: float
    normalized_mae: float
    shuffled_mae: float

    @property
    def improvement(self) -> float:
        return self.zero_mae - self.normalized_mae

    @property
    def beats_zero(self) -> bool:
        return self.normalized_mae < self.zero_mae

    @property
    def beats_shuffled(self) -> bool:
        return self.normalized_mae < self.shuffled_mae


class SeedInvariantPredictor:
    """Leave-one-seed-out prediction after per-seed state normalization."""

    def __init__(self, history_length: int = 2, ridge: float = 1e-6):
        if history_length < 2:
            raise ValueError("history_length must be >= 2")
        if ridge < 0:
            raise ValueError("ridge must be >= 0")
        self.history_length = history_length
        self.ridge = ridge

    def evaluate(
        self,
        records_by_seed: dict[int, Sequence[MemoryRecord]],
        train_seeds: Sequence[int],
        target_seed: int,
    ) -> SeedInvariantResult:
        if target_seed in train_seeds or not train_seeds:
            raise ValueError("target_seed must be excluded and train_seeds non-empty")

        def rows(seed: int, train: bool):
            split = _split(records_by_seed[seed], self.history_length)
            return split[0] if train else split[1]

        train_rows = []
        for seed in train_seeds:
            seed_rows = rows(seed, True)
            if not seed_rows:
                continue
            x = np.asarray([np.concatenate(r[1]) for r in seed_rows], dtype=float)
            mean, scale = x.mean(0), x.std(0)
            scale[scale == 0] = 1.0
            for r, v in zip(seed_rows, (x - mean) / scale):
                train_rows.append((v, r[2]))

        test_rows = rows(target_seed, False)
        if not train_rows or not test_rows:
            return SeedInvariantResult(
                tuple(train_seeds), target_seed, self.history_length, 0, 0.0, 0.0, 0.0
            )

        # Target-seed features are normalized using target-seed test-window statistics
        # only to remove representation scale; no target labels are used.
        test_raw = np.asarray([np.concatenate(r[1]) for r in test_rows], dtype=float)
        tmean, tscale = test_raw.mean(0), test_raw.std(0)
        tscale[tscale == 0] = 1.0
        test_x = (test_raw - tmean) / tscale

        train_x = np.asarray([r[0] for r in train_rows], dtype=float)
        y = np.asarray([r[1] for r in train_rows], dtype=float)
        actual = np.asarray([r[2] for r in test_rows], dtype=float)

        mean, scale = train_x.mean(0), train_x.std(0)
        scale[scale == 0] = 1.0
        x = (train_x - mean) / scale
        v = (test_x - mean) / scale

        design = np.column_stack((np.ones(len(x)), x))
        reg = np.eye(design.shape[1])
        reg[0, 0] = 0.0
        coef = np.linalg.solve(
            design.T @ design + self.ridge * reg,
            design.T @ y,
        )
        pred = np.column_stack((np.ones(len(v)), v)) @ coef

        shuffled = v.copy()
        np.random.default_rng(390001).shuffle(shuffled)
        shuffled_pred = np.column_stack((np.ones(len(shuffled)), shuffled)) @ coef

        return SeedInvariantResult(
            tuple(train_seeds),
            target_seed,
            self.history_length,
            len(actual),
            float(np.mean(np.abs(actual))),
            float(np.mean(np.abs(actual - pred))),
            float(np.mean(np.abs(actual - shuffled_pred))),
        )
