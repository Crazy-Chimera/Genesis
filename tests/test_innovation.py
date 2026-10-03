import pytest

from genesis.innovation import InnovationPredictor
from genesis.memory import MemoryRecord


def rec(t, y):
    return MemoryRecord(
        tick=t, identity=1, cells=((0, 0),), coherence=y,
        boundary_contrast=0.0, lifetime=t + 1, persistence=t + 1, overlap=1.0,
    )


def test_innovation_predictor_beats_zero_on_synthetic_ar():
    values = [0.2]
    for _ in range(80):
        values.append(values[-1] + 0.001)
    result = InnovationPredictor(history_length=3).evaluate(
        [rec(i, value) for i, value in enumerate(values)]
    )
    assert result.samples > 0
    assert result.innovation_mae < result.zero_mae


def test_innovation_requires_consecutive_ticks():
    assert InnovationPredictor().evaluate([rec(i * 2, 0.2 + i * 0.01) for i in range(20)]).samples == 0


def test_innovation_rejects_invalid_configuration():
    with pytest.raises(ValueError):
        InnovationPredictor(history_length=0)
    with pytest.raises(ValueError):
        InnovationPredictor(ridge=-1)
