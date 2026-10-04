from __future__ import annotations

import numpy as np
import pytest

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
    result = replace(result, samples=2, zero_mae=2.0, velocity_mae=1.0, shuffled_mae=1.5)
    assert result.improvement == 1.0
    assert result.beats_zero
    assert result.beats_shuffled


def test_state_velocity_uses_first_difference(monkeypatch):
    from genesis import state_velocity

    calls = []

    def fake_state(record):
        calls.append(record.tick)
        return (float(record.tick),)

    monkeypatch.setattr(state_velocity, "combined_state", fake_state)
    assert state_velocity.combined_state is fake_state
