from __future__ import annotations

import pytest

from genesis.memory import MemoryRecord
from genesis.state_velocity import StateVelocityPredictor


def test_state_velocity_validates_history_and_ridge():
    with pytest.raises(ValueError):
        StateVelocityPredictor(history_length=0)
    with pytest.raises(ValueError):
        StateVelocityPredictor(ridge=-1.0)
    with pytest.raises(ValueError):
        StateVelocityPredictor(train_fraction=0.0)


def test_state_velocity_empty_records():
    result = StateVelocityPredictor(history_length=2).evaluate([])
    assert result.samples == 0


def test_state_velocity_result_properties():
    from dataclasses import replace

    result = StateVelocityPredictor(history_length=1).evaluate([])
    result = replace(
        result, samples=2, zero_mae=2.0, velocity_mae=1.0, shuffled_mae=1.5
    )
    assert result.improvement == 1.0
    assert result.beats_zero
    assert result.beats_shuffled


def test_state_velocity_synthetic_first_difference_predicts_target(monkeypatch):
    import genesis.state_velocity as module

    def fake_state(record: MemoryRecord) -> tuple[float]:
        return (float(record.tick % 2),)

    monkeypatch.setattr(module, "combined_state", fake_state)

    records = []
    coherence = 0.0
    previous_state = 0.0
    for tick in range(60):
        state = float(tick % 2)
        if tick:
            coherence += state - previous_state
        previous_state = state
        records.append(
            MemoryRecord(
                tick=tick,
                identity=1,
                cells=((0, 0),),
                coherence=coherence,
                boundary_contrast=0.0,
                lifetime=tick + 1,
                persistence=tick + 1,
                overlap=1.0,
            )
        )

    result = StateVelocityPredictor(history_length=1).evaluate(records)
    assert result.samples > 0
    assert result.beats_zero
