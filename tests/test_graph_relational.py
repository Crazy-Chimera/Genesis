import pytest

from genesis.graph_relational import GraphRelationalPredictor, GRAPH_RELATIONAL_WIDTH
from genesis.memory import MemoryRecord


def rec(t, y, graph):
    return MemoryRecord(
        tick=t,
        identity=1,
        cells=((0, 0),),
        coherence=y,
        boundary_contrast=0.0,
        lifetime=t + 1,
        persistence=t + 1,
        overlap=1.0,
        graph_relational=graph,
    )


def test_graph_relational_predictor_beats_baseline_on_synthetic_relation():
    rows = [
        tuple([float(t)] + [0.0] * (GRAPH_RELATIONAL_WIDTH - 1))
        for t in range(81)
    ]
    result = GraphRelationalPredictor().evaluate(
        [rec(t, 0.2 + 0.01 * t, row) for t, row in enumerate(rows)]
    )
    assert result.samples > 0
    assert result.graph_mae < result.baseline_mae


def test_graph_relational_requires_exact_consecutive_ticks():
    row = (0.0,) * GRAPH_RELATIONAL_WIDTH
    records = [rec(t, 0.1, row) for t in range(0, 20, 2)]
    assert GraphRelationalPredictor().evaluate(records).samples == 0


def test_graph_relational_rejects_invalid_configuration():
    with pytest.raises(ValueError):
        GraphRelationalPredictor(max_peers=0)
    with pytest.raises(ValueError):
        GraphRelationalPredictor(ridge=-1)


def test_graph_relational_width_is_fixed():
    assert GRAPH_RELATIONAL_WIDTH == 33
