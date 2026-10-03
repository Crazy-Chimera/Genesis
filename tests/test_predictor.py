import pytest

from genesis.memory import MemoryRecord
from genesis.predictor import PredictiveMemory, linear_history_predict, persistence_predict


def record(tick: int, coherence: float, identity: int = 1) -> MemoryRecord:
    return MemoryRecord(
        tick=tick, identity=identity, cells=((0, 0),),
        coherence=coherence, boundary_contrast=0.0,
        lifetime=tick + 1, persistence=tick + 1, overlap=1.0,
    )


def test_persistence_predictor_uses_last_observation():
    assert persistence_predict([record(0, 0.2), record(1, 0.4)]) == pytest.approx(0.4)


def test_linear_history_predictor_follows_linear_trend():
    history = [record(0, 0.2), record(1, 0.4), record(2, 0.6)]
    assert linear_history_predict(history) == pytest.approx(0.8)


def test_predictive_memory_history_beats_persistence_on_linear_trace():
    records = [record(tick, 0.2 + 0.1 * tick) for tick in range(6)]
    result = PredictiveMemory().evaluate(records, history_length=3)
    assert result.samples == 5
    assert result.history_mae < result.baseline_mae
    assert result.improvement > 0.0


def test_predictive_memory_does_not_mutate_records():
    records = [record(tick, 0.2 + 0.1 * tick) for tick in range(4)]
    before = tuple(records)
    PredictiveMemory().evaluate(records)
    assert tuple(records) == before


def test_predictive_memory_rejects_invalid_history_length():
    with pytest.raises(ValueError):
        PredictiveMemory().evaluate([record(0, 0.2)], history_length=0)
