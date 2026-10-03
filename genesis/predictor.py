from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Sequence

from .memory import MemoryRecord

Feature = Callable[[MemoryRecord], float]


@dataclass(frozen=True)
class PredictionResult:
    """Comparison of a persistence baseline with a history-based predictor."""

    samples: int
    baseline_mae: float
    history_mae: float

    @property
    def improvement(self) -> float:
        return self.baseline_mae - self.history_mae

    @property
    def history_beats_baseline(self) -> bool:
        return self.history_mae < self.baseline_mae


def coherence_feature(record: MemoryRecord) -> float:
    return record.coherence


def size_feature(record: MemoryRecord) -> float:
    return float(len(record.cells))


def persistence_predict(
    history: Sequence[MemoryRecord],
    feature: Feature = coherence_feature,
) -> float:
    if not history:
        raise ValueError("history must contain at least one record")
    return float(feature(history[-1]))
def linear_history_predict(
    history: Sequence[MemoryRecord],
    feature: Feature = coherence_feature,
) -> float:
    """Extrapolate one step from the most recent history using linear trend."""
    if not history:
        raise ValueError("history must contain at least one record")
    if len(history) == 1:
        return feature(history[-1])

    x = [float(record.tick) for record in history]
    y = [float(feature(record)) for record in history]
    x_mean = sum(x) / len(x)
    y_mean = sum(y) / len(y)
    denominator = sum((value - x_mean) ** 2 for value in x)
    if denominator == 0.0:
        return y[-1]

    slope = sum((xi - x_mean) * (yi - y_mean) for xi, yi in zip(x, y)) / denominator
    return y[-1] + slope * (x[-1] - x[-2])


class PredictiveMemory:
    """External prediction layer over observer-level temporal memory."""

    def __init__(self, feature: Feature = coherence_feature) -> None:
        self.feature = feature

    def evaluate(
        self,
        records: Iterable[MemoryRecord],
        history_length: int = 3,
    ) -> PredictionResult:
        if history_length < 1:
            raise ValueError("history_length must be >= 1")

        by_identity: dict[int, list[MemoryRecord]] = {}
        for item in records:
            by_identity.setdefault(item.identity, []).append(item)

        baseline_errors: list[float] = []
        history_errors: list[float] = []

        for history in by_identity.values():
            ordered = sorted(history, key=lambda item: item.tick)
            for index in range(1, len(ordered)):
                target = ordered[index]
                available = ordered[max(0, index - history_length):index]
                baseline = persistence_predict(available, self.feature)
                prediction = linear_history_predict(available, self.feature)
                actual = self.feature(target)
                baseline_errors.append(abs(actual - baseline))
                history_errors.append(abs(actual - prediction))

        samples = len(baseline_errors)
        if samples == 0:
            return PredictionResult(0, 0.0, 0.0)

        return PredictionResult(
            samples=samples,
            baseline_mae=sum(baseline_errors) / samples,
            history_mae=sum(history_errors) / samples,
        )
