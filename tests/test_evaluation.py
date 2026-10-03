import pytest

from genesis.evaluation import (
    PredictiveEvaluator,
    mean_history_predict,
    shuffled_history_predict,
)
from genesis.memory import MemoryRecord


def record(tick: int, coherence: float, identity: int = 1) -> MemoryRecord:
    return MemoryRecord(
        tick=tick,
        identity=identity,
        cells=((0, 0),),
        coherence=coherence,
        boundary_contrast=0.0,
        lifetime=tick + 1,
        persistence=tick + 1,
        overlap=1.0,
    )


def test_shuffled_predictor_preserves_feature_values():
    history = [record(0, 0.2), record(1, 0.4), record(2, 0.6)]
    prediction = shuffled_history_predict(history, seed=7)
    assert isinstance(prediction, float)


def test_mean_predictor_returns_history_average():
    history = [record(0, 0.2), record(1, 0.4), record(2, 0.6)]
    assert mean_history_predict(history) == pytest.approx(0.4)


def test_evaluator_uses_future_holdout_and_consecutive_ticks():
    records = [record(tick, 0.2 + 0.1 * tick) for tick in range(10)]
    result = PredictiveEvaluator(
        history_length=3,
        train_fraction=0.5,
        require_consecutive=True,
    ).evaluate(records)

    assert result.heldout_start_tick == 4
    assert result.samples == 6
    assert result.history_mae < result.baseline_mae
    assert result.mean_mae > 0.0


def test_evaluator_rejects_invalid_configuration():
    with pytest.raises(ValueError):
        PredictiveEvaluator(history_length=0)
    with pytest.raises(ValueError):
        PredictiveEvaluator(train_fraction=0.0)
    with pytest.raises(ValueError):
        PredictiveEvaluator(train_fraction=1.0)


def test_evaluator_rejects_non_consecutive_targets_when_requested():
    records = [
        record(0, 0.2),
        record(1, 0.3),
        record(3, 0.5),
        record(4, 0.6),
        record(6, 0.8),
    ]
    result = PredictiveEvaluator(
        history_length=2,
        train_fraction=0.4,
        require_consecutive=True,
    ).evaluate(records)
    assert result.samples == 0


def test_evaluator_does_not_mutate_records():
    records = [record(tick, 0.2 + 0.1 * tick) for tick in range(8)]
    before = tuple(records)
    PredictiveEvaluator().evaluate(records)
    assert tuple(records) == before
