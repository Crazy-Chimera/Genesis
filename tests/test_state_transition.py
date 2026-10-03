from __future__ import annotations

from genesis.memory import MemoryRecord
from genesis.state_transition import (
    TRANSITION_WIDTH,
    StateTransitionPredictor,
    transition_state,
)


def make_record(tick: int, identity: int = 1, coherence: float = 0.0) -> MemoryRecord:
    return MemoryRecord(
        tick=tick,
        identity=identity,
        cells=((0, 0),),
        coherence=coherence,
        boundary_contrast=0.0,
        lifetime=tick + 1,
        persistence=tick + 1,
        overlap=1.0,
        local_patch=(0.0,) * 9,
        phase_patch=(0.0,) * 18,
        gradient_patch=(0.0,) * 18,
        motion=(0.0,) * 3,
        boundary_flux=(0.0,) * 5,
        spatial_field=(0.0,) * 18,
        multiscale_field=(0.0,) * 68,
        relational=(0.0,) * 16,
        graph_relational=(0.0,) * 33,
    )


def test_transition_state_is_compact_and_deterministic():
    previous = make_record(tick=0, identity=1)
    current = make_record(tick=1, identity=1)

    first = transition_state(previous, current)
    second = transition_state(previous, current)

    assert len(first) == TRANSITION_WIDTH
    assert first == second


def test_transition_predictor_beats_zero_on_synthetic_data():
    records = []
    for tick in range(30):
        records.append(make_record(tick=tick, identity=1, coherence=0.5 + 0.01 * tick))

    result = StateTransitionPredictor().evaluate(records)
    assert result.samples > 0
    assert result.transition_mae < result.zero_mae


def test_transition_predictor_rejects_invalid_configuration():
    try:
        StateTransitionPredictor(train_fraction=0.0)
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError")
