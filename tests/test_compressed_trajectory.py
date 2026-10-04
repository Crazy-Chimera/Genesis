import pytest

from genesis.compressed_trajectory import CompressedStateTrajectoryPredictor
from genesis.memory import MemoryRecord


def rec(t, c):
    zeros = {
        "local_patch": (0.0,) * 9,
        "phase_patch": (0.0,) * 18,
        "gradient_patch": (0.0,) * 18,
        "motion": (0.0,) * 3,
        "boundary_flux": (0.0,) * 5,
        "spatial_field": (0.0,) * 18,
        "multiscale_field": (0.0,) * 68,
        "relational": (0.0,) * 16,
        "graph_relational": (0.0,) * 33,
    }
    return MemoryRecord(
        tick=t,
        identity=1,
        cells=((0, 0),),
        coherence=c,
        boundary_contrast=0.0,
        lifetime=t + 1,
        persistence=t + 1,
        overlap=1.0,
        **zeros,
    )


def test_compressed_trajectory_reconstructs_low_dimensional_signal():
    records = [rec(t, 0.1 + 0.0001 * t * t) for t in range(81)]
    result = CompressedStateTrajectoryPredictor(
        history_length=3, components=4
    ).evaluate(records)
    assert result.samples > 0
    assert result.trajectory_mae < result.zero_mae


def test_compressed_trajectory_requires_consecutive_ticks():
    records = [rec(t, 0.1) for t in (0, 1, 3, 4, 6, 7, 9, 10)]
    result = CompressedStateTrajectoryPredictor(
        history_length=3, components=4
    ).evaluate(records)
    assert result.samples == 0


def test_compressed_trajectory_rejects_invalid_configuration():
    with pytest.raises(ValueError):
        CompressedStateTrajectoryPredictor(history_length=1)
    with pytest.raises(ValueError):
        CompressedStateTrajectoryPredictor(components=0)
    with pytest.raises(ValueError):
        CompressedStateTrajectoryPredictor(ridge=-1)
