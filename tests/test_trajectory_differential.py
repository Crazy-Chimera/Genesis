from __future__ import annotations

import numpy as np

from genesis.memory import MemoryRecord
from genesis.trajectory_differential import (
    TrajectoryDifferentialPredictor,
    differential_trajectory,
)


def record(tick: int, coherence: float, offset: float) -> MemoryRecord:
    return MemoryRecord(
        tick=tick,
        identity=1,
        cells=((0, 0),),
        coherence=coherence,
        boundary_contrast=0.0,
        lifetime=tick + 1,
        persistence=1.0,
        overlap=1.0,
        local_patch=(offset,) * 9,
        phase_patch=(offset,) * 18,
        gradient_patch=(offset,) * 18,
        motion=(offset,) * 3,
        boundary_flux=(offset,) * 5,
        boundary_deformation=(offset,) * 7,
        spatiotemporal_patch=(offset,) * 36,
        spatial_field=(offset,) * 18,
        multiscale_field=(offset,) * 68,
        relational=(offset,) * 16,
        graph_relational=(offset,) * 33,
    )


def test_differential_trajectory_is_finite_and_compact():
    items = [record(0, 0.1, 0.0), record(1, 0.2, 1.0), record(2, 0.3, 2.0)]
    values = differential_trajectory(items, 3)
    assert len(values) == 15
    assert np.isfinite(values).all()


def test_predictor_rejects_invalid_history():
    try:
        TrajectoryDifferentialPredictor(history_length=1)
    except ValueError:
        pass
    else:
        raise AssertionError("history_length=1 must fail")


def test_predictor_empty_records():
    result = TrajectoryDifferentialPredictor().evaluate([])
    assert result.samples == 0
