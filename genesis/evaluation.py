from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Iterable

from .memory import MemoryRecord
from .predictor import Feature, coherence_feature, linear_history_predict, persistence_predict


@dataclass(frozen=True)
class EvaluationResult:
    """Walk-forward evaluation on a future portion of an observed trajectory."""

    samples: int
    baseline_mae: float
    history_mae: float
    shuffled_mae: float
    heldout_start_tick: int
    history_length: int

    @property
    def improvement(self) -> float:
        return self.baseline_mae - self.history_mae

    @property
    def beats_baseline(self) -> bool:
        return self.history_mae < self.baseline_mae

    @property
    def beats_shuffled(self) -> bool:
        return self.history_mae < self.shuffled_mae


def shuffled_history_predict(
    history: list[MemoryRecord],
    feature: Feature = coherence_feature,
    seed: int = 0,
) -> float:
    """Predict from a deterministic permutation of the same history values."""
    if not history:
        raise ValueError("history must contain at least one record")

    shuffled = list(history)
    random.Random(seed).shuffle(shuffled)
    return linear_history_predict(shuffled, feature)


class PredictiveEvaluator:
    """External, walk-forward evaluation of predictive information.

    The evaluator never modifies universe or memory state. Evaluation begins
    strictly after a chronological holdout boundary and can require exact
    one-tick spacing to avoid silently treating missing observations as
    adjacent time steps.
    """

    def __init__(
        self,
        feature: Feature = coherence_feature,
        history_length: int = 3,
        train_fraction: float = 0.5,
        require_consecutive: bool = True,
        shuffle_seed: int = 390001,
    ) -> None:
        if history_length < 1:
            raise ValueError("history_length must be >= 1")
        if not 0.0 < train_fraction < 1.0:
            raise ValueError("train_fraction must be between 0 and 1")
        self.feature = feature
        self.history_length = history_length
        self.train_fraction = train_fraction
        self.require_consecutive = require_consecutive
        self.shuffle_seed = shuffle_seed

    def evaluate(self, records: Iterable[MemoryRecord]) -> EvaluationResult:
        ordered = sorted(records, key=lambda item: (item.tick, item.identity))
        if not ordered:
            return EvaluationResult(0, 0.0, 0.0, 0.0, 0, self.history_length)

        max_tick = ordered[-1].tick
        min_tick = ordered[0].tick
        heldout_start = min_tick + max(
            1,
            int((max_tick - min_tick) * self.train_fraction),
        )

        by_identity: dict[int, list[MemoryRecord]] = {}
        for item in ordered:
            by_identity.setdefault(item.identity, []).append(item)

        baseline_errors: list[float] = []
        history_errors: list[float] = []
        shuffled_errors: list[float] = []

        for identity_records in by_identity.values():
            identity_records.sort(key=lambda item: item.tick)
            for index, target in enumerate(identity_records):
                if target.tick < heldout_start or index < self.history_length:
                    continue

                history = identity_records[index - self.history_length:index]
                if self.require_consecutive:
                    expected = list(
                        range(target.tick - self.history_length, target.tick)
                    )
                    if [item.tick for item in history] != expected:
                        continue

                actual = self.feature(target)
                baseline = persistence_predict(history, self.feature)
                prediction = linear_history_predict(history, self.feature)
                shuffled = shuffled_history_predict(
                    history,
                    self.feature,
                    seed=self.shuffle_seed + target.tick + target.identity,
                )

                baseline_errors.append(abs(actual - baseline))
                history_errors.append(abs(actual - prediction))
                shuffled_errors.append(abs(actual - shuffled))

        samples = len(baseline_errors)
        if samples == 0:
            return EvaluationResult(
                0, 0.0, 0.0, 0.0, heldout_start, self.history_length
            )

        return EvaluationResult(
            samples=samples,
            baseline_mae=sum(baseline_errors) / samples,
            history_mae=sum(history_errors) / samples,
            shuffled_mae=sum(shuffled_errors) / samples,
            heldout_start_tick=heldout_start,
            history_length=self.history_length,
        )
