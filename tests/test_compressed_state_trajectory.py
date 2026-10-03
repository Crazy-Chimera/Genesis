import pytest

from genesis.compressed_state_trajectory import CompressedStateTrajectoryPredictor
from genesis.memory import MemoryRecord


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


def test_compressed_trajectory_reconstructs_linear_innovation():
    records = [
        rec(t, 0.1 + 0.001 * t * t, (float(t),) + (0.0,) * 17)
        for t in range(81)
    ]
    result = CompressedStateTrajectoryPredictor(
        feature_name="spatial_field",
        history_length=3,
        components=2,
    ).evaluate(records)
    assert result.samples > 0
    assert result.trajectory_mae < result.zero_mae


def test_compressed_trajectory_requires_consecutive_ticks():
    records = [
        rec(t, 0.1, (float(t),) + (0.0,) * 17)
        for t in (0, 1, 3, 4, 6, 7, 9, 10)
    ]
    result = CompressedStateTrajectoryPredictor(
        feature_name="spatial_field", history_length=3, components=2
    ).evaluate(records)
    assert result.samples == 0


def test_compressed_trajectory_rejects_invalid_configuration():
    with pytest.raises(ValueError):
        CompressedStateTrajectoryPredictor(history_length=1)
    with pytest.raises(ValueError):
        CompressedStateTrajectoryPredictor(components=0)
    with pytest.raises(ValueError):
        CompressedStateTrajectoryPredictor(
            feature_name="spatial_field", components=19
        )
    with pytest.raises(ValueError):
        CompressedStateTrajectoryPredictor(ridge=-1)
