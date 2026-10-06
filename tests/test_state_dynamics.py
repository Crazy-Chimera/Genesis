from __future__ import annotations

from genesis.state_dynamics import StateDynamicsPredictor


def test_state_dynamics_rejects_short_history():
    try:
        StateDynamicsPredictor(history_length=1)
    except ValueError:
        return
    raise AssertionError("history_length=1 must be rejected")


def test_state_dynamics_rejects_invalid_ridge():
    try:
        StateDynamicsPredictor(ridge=-1.0)
    except ValueError:
        return
    raise AssertionError("negative ridge must be rejected")
