from __future__ import annotations

from genesis.state_delta_trajectory import StateDeltaTrajectoryPredictor


def test_delta_trajectory_rejects_invalid_history() -> None:
    try:
        StateDeltaTrajectoryPredictor(history_length=1)
    except ValueError as exc:
        assert "history_length" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_delta_trajectory_rejects_unknown_feature() -> None:
    try:
        StateDeltaTrajectoryPredictor(feature_name="missing")
    except ValueError as exc:
        assert "unknown state feature" in str(exc)
    else:
        raise AssertionError("expected ValueError")
