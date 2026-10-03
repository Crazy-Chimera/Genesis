import pytest
from genesis.memory import MemoryRecord
from genesis.state_trajectory import StateTrajectoryPredictor


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


def test_state_trajectory_reconstructs_linear_innovation():
    records = [
        rec(t, 0.1 + 0.001 * t * t, (float(t),) + (0.0,) * 17)
        for t in range(81)
    ]
    r = StateTrajectoryPredictor(
        history_length=3, feature_name="spatial_field"
    ).evaluate(records)
    assert r.samples > 0 and r.trajectory_mae < r.zero_mae


def test_state_trajectory_requires_consecutive_ticks():
    records = [
        rec(t, 0.1, (float(t),) + (0.0,) * 17)
        for t in (0, 1, 3, 4, 6, 7, 9, 10)
    ]
    assert (
        StateTrajectoryPredictor(
            history_length=3, feature_name="spatial_field"
        ).evaluate(records).samples
        == 0
    )


def test_state_trajectory_rejects_invalid_configuration():
    with pytest.raises(ValueError):
        StateTrajectoryPredictor(history_length=1)
    with pytest.raises(ValueError):
        StateTrajectoryPredictor(ridge=-1)
    with pytest.raises(ValueError):
        StateTrajectoryPredictor(feature_name="unknown")
