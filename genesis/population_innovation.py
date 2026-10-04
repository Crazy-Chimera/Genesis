from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

from .memory import MemoryRecord


@dataclass(frozen=True)
class PopulationInnovationEvaluationResult:
    samples: int
    zero_mae: float
    population_mae: float
    shuffled_mae: float
    heldout_start_tick: int

    @property
    def improvement(self) -> float:
        return self.zero_mae - self.population_mae

    @property
    def beats_zero(self) -> bool:
        return self.population_mae < self.zero_mae

    @property
    def beats_shuffled(self) -> bool:
        return self.population_mae < self.shuffled_mae


def population_state(records: Iterable[MemoryRecord]) -> tuple[int, tuple[float, ...]]:
    items = list(records)
    if not items:
        return 0, (0.0,) * 12

    sizes = np.asarray([len(r.cells) for r in items], dtype=float)
    boundaries = np.asarray([r.boundary_contrast for r in items], dtype=float)
    lifetimes = np.asarray([r.lifetime for r in items], dtype=float)
    persistence = np.asarray([r.persistence for r in items], dtype=float)
    overlaps = np.asarray([r.overlap for r in items], dtype=float)
    motion = np.asarray([np.linalg.norm(r.motion) for r in items], dtype=float)
    flux = np.asarray([np.linalg.norm(r.boundary_flux) for r in items], dtype=float)
    relational = np.asarray([np.linalg.norm(r.relational) for r in items], dtype=float)

    return items[0].tick, (
        float(len(items)),
        float(sizes.sum()),
        float(sizes.mean()),
        float(sizes.std()),
        float(boundaries.mean()),
        float(lifetimes.mean()),
        float(persistence.mean()),
        float(overlaps.mean()),
        float(motion.mean()),
        float(flux.mean()),
        float(relational.mean()),
        float(sizes.max()),
    )


class PopulationInnovationPredictor:
    """Predict next global coherence innovation from the current population state."""

    def __init__(
        self,
        train_fraction: float = 0.5,
        ridge: float = 1e-6,
        require_consecutive: bool = True,
    ) -> None:
        if not 0.0 < train_fraction < 1.0:
            raise ValueError("train_fraction must be between 0 and 1")
        if ridge < 0.0:
            raise ValueError("ridge must be >= 0")
        self.train_fraction = train_fraction
        self.ridge = ridge
        self.require_consecutive = require_consecutive

    def evaluate(self, records: Iterable[MemoryRecord]) -> PopulationInnovationEvaluationResult:
        by_tick: dict[int, list[MemoryRecord]] = {}
        for record in records:
            by_tick.setdefault(record.tick, []).append(record)
        ticks = sorted(by_tick)
        if len(ticks) < 2:
            return PopulationInnovationEvaluationResult(0, 0.0, 0.0, 0.0, 0)

        states = dict(population_state(by_tick[t]) for t in ticks)
        coherences = {
            t: float(np.mean([r.coherence for r in by_tick[t]])
        )
        min_tick, max_tick = ticks[0], ticks[-1]
        heldout = min_tick + max(1, int((max_tick - min_tick) * self.train_fraction))

        train_x: list[tuple[float, ...]] = []
        train_y: list[float] = []
        test_x: list[tuple[float, ...]] = []
        test_y: list[float] = []

        for current, target in zip(ticks, ticks[1:]):
            if self.require_consecutive and target != current + 1:
                continue
            delta = coherences[target] - coherences[current]
            row = states[current][1]
            if target < heldout:
                train_x.append(row)
                train_y.append(delta)
            else:
                test_x.append(row)
                test_y.append(delta)

        if not train_x or not test_x:
            return PopulationInnovationEvaluationResult(0, 0.0, 0.0, 0.0, heldout)

        train = np.asarray(train_x, dtype=float)
        test = np.asarray(test_x, dtype=float)
        y = np.asarray(train_y, dtype=float)
        mean = train.mean(axis=0)
        scale = np.asarray(train.std(axis=0), dtype=float)
        scale[scale == 0.0] = 1.0

        design = np.column_stack((np.ones(len(train)), (train - mean) / scale))
        reg = np.eye(design.shape[1])
        reg[0, 0] = 0.0
        coef = np.linalg.solve(design.T @ design + self.ridge * reg, design.T @ y)

        pred = np.column_stack((np.ones(len(test)), (test - mean) / scale)) @ coef
        shuffled = test.copy()
        np.random.default_rng(390001).shuffle(shuffled)
        shuffled_pred = np.column_stack(
            (np.ones(len(shuffled)), (shuffled - mean) / scale)
        ) @ coef

        actual = np.asarray(test_y, dtype=float)
        return PopulationInnovationEvaluationResult(
            samples=len(actual),
            zero_mae=float(np.mean(np.abs(actual))),
            population_mae=float(np.mean(np.abs(actual - pred))),
            shuffled_mae=float(np.mean(np.abs(actual - shuffled_pred))),
            heldout_start_tick=heldout,
        )
