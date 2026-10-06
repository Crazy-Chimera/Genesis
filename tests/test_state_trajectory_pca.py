import numpy as np
import pytest

from genesis.memory import MemoryRecord
from genesis.state_trajectory_pca import StateTrajectoryPCAPredictor


def record(tick, value):
    return MemoryRecord(
        tick=tick,
        identity=1,
        cells=((0, 0),),
        coherence=value,
        boundary_contrast=0.0,
        lifetime=tick + 1,
        persistence=1.0,
        overlap=1.0,
        local_patch=(value,) * 9,
        phase_patch=(value,) * 18,
        gradient_patch=(value,) * 18,
        motion=(value,) * 3,
        boundary_flux=(value,) * 5,
        boundary_deformation=(value,) * 7,
        spatiotemporal_patch=(value,) * 36,
        spatial_field=(value,) * 18,
        multiscale_field=(value,) * 68,
        relational=(value,) * 16,
        graph_relational=(value,) * 33,
        global_harmonics=(value,) * 9,
    )


def test_pca_trajectory_validation():
    with pytest.raises(ValueError):
        StateTrajectoryPCAPredictor(history_length=1)
    with pytest.raises(ValueError):
        StateTrajectoryPCAPredictor(components=0)


def test_pca_trajectory_predictor_is_deterministic():
    records = [record(t, 0.1 + 0.001 * t) for t in range(20)]
    predictor = StateTrajectoryPCAPredictor(history_length=3, components=2)
    first = predictor.evaluate(records)
    second = predictor.evaluate(records)
    assert first == second
    assert first.samples > 0
