from __future__ import annotations

from genesis.state_transition import (
    TRANSITION_WIDTH,
    StateTransitionPredictor,
    transition_state,
)
from tests.conftest import make_record


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
        previous = make_record(tick=tick, identity=1)
        current = make_record(tick=tick + 1, identity=1)
        current = current.__class__(
            **{**current.__dict__, "coherence": 0.5 + 0.01 * tick}
        )
        records.append(current)

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
