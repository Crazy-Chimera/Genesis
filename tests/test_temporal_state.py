import pytest

from genesis.temporal_state import TemporalStatePredictor


def test_delta_requires_history():
    with pytest.raises(ValueError):
        TemporalStatePredictor(mode="delta", history_length=1)


def test_acceleration_requires_three_states():
    with pytest.raises(ValueError):
        TemporalStatePredictor(mode="acceleration", history_length=2)


def test_unknown_mode_rejected():
    with pytest.raises(ValueError):
        TemporalStatePredictor(mode="unknown")


def test_unknown_feature_rejected():
    with pytest.raises(ValueError):
        TemporalStatePredictor(feature_name="missing")


def test_invalid_ridge_rejected():
    with pytest.raises(ValueError):
        TemporalStatePredictor(ridge=-1.0)


def test_incomplete_feature_window_is_skipped():
    from genesis.memory import MemoryRecord

    records = [
        MemoryRecord(
            tick=tick,
            identity=1,
            cells=((0, 0),),
            coherence=0.1 * tick,
            boundary_contrast=0.0,
            lifetime=tick + 1,
            persistence=tick + 1,
            overlap=1.0,
        )
        for tick in range(5)
    ]
    result = TemporalStatePredictor(history_length=2).evaluate(records)
    assert result.samples == 0
