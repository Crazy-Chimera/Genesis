from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
import numpy as np

from .memory import MemoryRecord
from .state_innovation import STATE_FEATURES_WITH_COMBINED


@dataclass(frozen=True)
class StateTrajectoryPCAResult:
    samples: int
    zero_mae: float
    pca_mae: float
    shuffled_mae: float
    components: int
    history_length: int

    @property
    def improvement(self) -> float:
        return self.zero_mae - self.pca_mae

    @property
    def beats_zero(self) -> bool:
        return self.pca_mae < self.zero_mae

    @property
    def beats_shuffled(self) -> bool:
        return self.pca_mae < self.shuffled_mae


class StateTrajectoryPCAPredictor:
    """Predict next coherence innovation from a PCA-compressed state trajectory."""

    def __init__(
        self,
        feature_name: str = "combined",
        history_length: int = 3,
        components: int = 8,
        train_fraction: float = 0.5,
        ridge: float = 1e-6,
        require_consecutive: bool = True,
    ) -> None:
        if history_length < 2:
            raise ValueError("history_length must be >= 2")
        if components < 1:
            raise ValueError("components must be >= 1")
        if not 0.0 < train_fraction < 1.0:
            raise ValueError("train_fraction must be between 0 and 1")
        if ridge < 0.0:
            raise ValueError("ridge must be >= 0")
        matches = [s for s in STATE_FEATURES_WITH_COMBINED if s.name == feature_name]
        if not matches:
            raise ValueError(f"unknown state feature: {feature_name}")
        self.spec = matches[0]
        self.history_length = history_length
        self.components = components
        self.train_fraction = train_fraction
        self.ridge = ridge
        self.require_consecutive = require_consecutive

    def evaluate(self, records: Iterable[MemoryRecord]) -> StateTrajectoryPCAResult:
        ordered = sorted(records, key=lambda x: (x.tick, x.identity))
        if not ordered:
            return StateTrajectoryPCAResult(0, 0.0, 0.0, 0.0, self.components, self.history_length)

        lo, hi = ordered[0].tick, ordered[-1].tick
        heldout = lo + max(1, int((hi - lo) * self.train_fraction))
        groups: dict[int, list[MemoryRecord]] = {}
        for item in ordered:
            groups.setdefault(item.identity, []).append(item)

        train_x: list[tuple[float, ...]] = []
        train_y: list[float] = []
        test_x: list[tuple[float, ...]] = []
        test_y: list[float] = []

        for items in groups.values():
            items.sort(key=lambda x: x.tick)
            for i in range(self.history_length, len(items)):
                window = items[i - self.history_length:i]
                target = items[i]
                ticks = [x.tick for x in window] + [target.tick]
                if self.require_consecutive and any(
                    ticks[j + 1] != ticks[j] + 1 for j in range(len(ticks) - 1)
                ):
                    continue
                vectors = [np.asarray(self.spec.feature(x), dtype=float) for x in window]
                if any(v.size != self.spec.width for v in vectors):
                    continue
                row = np.concatenate(vectors)
                delta = target.coherence - window[-1].coherence
                if target.tick < heldout:
                    train_x.append(tuple(row))
                    train_y.append(delta)
                else:
                    test_x.append(tuple(row))
                    test_y.append(delta)

        if not train_x or not test_x:
            return StateTrajectoryPCAResult(0, 0.0, 0.0, 0.0, self.components, self.history_length)

        train = np.asarray(train_x)
        test = np.asarray(test_x)
        y = np.asarray(train_y)
        mean = train.mean(axis=0)
        scale = train.std(axis=0)
        scale[scale == 0] = 1
        z = (train - mean) / scale
        zv = (test - mean) / scale

        _, _, vt = np.linalg.svd(z, full_matrices=False)
        k = min(self.components, vt.shape[0])
        basis = vt[:k]
        reduced = z @ basis.T
        reduced_test = zv @ basis.T

        design = np.column_stack((np.ones(len(reduced)), reduced))
        reg = np.eye(design.shape[1])
        reg[0, 0] = 0
        coef = np.linalg.solve(
            design.T @ design + self.ridge * reg,
            design.T @ y,
        )

        prediction = np.column_stack(
            (np.ones(len(reduced_test)), reduced_test)
        ) @ coef

        shuffled = reduced_test.copy()
        np.random.default_rng(390001).shuffle(shuffled)
        shuffled_prediction = np.column_stack(
            (np.ones(len(shuffled)), shuffled)
        ) @ coef

        actual = np.asarray(test_y)
        return StateTrajectoryPCAResult(
            samples=len(actual),
            zero_mae=float(np.mean(np.abs(actual))),
            pca_mae=float(np.mean(np.abs(actual - prediction))),
            shuffled_mae=float(np.mean(np.abs(actual - shuffled_prediction))),
            components=k,
            history_length=self.history_length,
        )
