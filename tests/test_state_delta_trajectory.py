from __future__ import annotations

from genesis.memory import MemoryRecord
from genesis.state_delta_trajectory import StateDeltaTrajectoryPredictor


def rec(t, c, state):
    return MemoryRecord(
        tick=t,
        identity=1,
        cells=((0, 0),),
        coherence=c,
        boundary_contrast=0.0,
        lifetime=t + 1,
        persistence=t + 1,
        overlap=1.0,
        spatial_field=state,
    )


def test_delta_trajectory_reconstructs_innovation() -> None:
    records = [
        rec(t, 0.1 + 0.0001 * t**3, (float(t * t),) + (0.0,) * 17)
        for t in range(81)
    ]
    result = StateDeltaTrajectoryPredictor(
        feature_name="spatial_field",
        history_length=3,
    ).evaluate(records)
    assert result.samples > 0
    assert result.delta_mae < result.zero_mae


def test_delta_trajectory_requires_consecutive_ticks() -> None:
    records = [
        rec(t, 0.1, (float(t),) + (0.0,) * 17)
        for t in (0, 1, 3, 4, 6, 7, 9, 10)
    ]
    result = StateDeltaTrajectoryPredictor(
        feature_name="spatial_field",
        history_length=3,
    ).evaluate(records)
    assert result.samples == 0


def test_delta_trajectory_rejects_invalid_configuration() -> None:
    try:
        StateDeltaTrajectoryPredictor(history_length=1)
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError")

    try:
        StateDeltaTrajectoryPredictor(ridge=-1)
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError")

    try:
        StateDeltaTrajectoryPredictor(feature_name="missing")
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError")
