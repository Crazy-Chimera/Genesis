import pytest

from genesis.memory import MemoryRecord
from genesis.relational import CrossRegionRelationalPredictor


def rec(t, y, relation):
    return MemoryRecord(
        tick=t,
        identity=1,
        cells=((0, 0),),
        coherence=y,
        boundary_contrast=0.0,
        lifetime=t + 1,
        persistence=t + 1,
        overlap=1.0,
        relational=relation,
    )


def test_relational_predictor_beats_baseline_on_synthetic_relation():
    rows = [tuple([float(t)] + [0.0] * 15) for t in range(81)]
    result = CrossRegionRelationalPredictor().evaluate(
        [rec(t, 0.2 + 0.01 * t, row) for t, row in enumerate(rows)]
    )
    assert result.samples > 0
    assert result.relational_mae < result.baseline_mae


def test_relational_requires_exact_consecutive_ticks():
    rows = [(0.0,) * 16] * 10
    records = [rec(t, 0.1, row) for t, row in zip((0, 1, 3, 4, 6, 7, 9, 10, 12, 13), rows)]
    assert CrossRegionRelationalPredictor().evaluate(records).samples == 0


def test_relational_rejects_invalid_configuration():
    with pytest.raises(ValueError):
        CrossRegionRelationalPredictor(max_peers=0)
    with pytest.raises(ValueError):
        CrossRegionRelationalPredictor(ridge=-1)
