from __future__ import annotations

import numpy as np
import pytest

from genesis.latent_trajectory import LatentTrajectoryPredictor
from genesis.memory import MemoryRecord


def record(tick: int, value: float) -> MemoryRecord:
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
    )


def test_latent_trajectory_beats_zero_on_synthetic_relation():
    records = [record(i, 0.2 + 0.01 * i + 0.001 * i * i) for i in range(40)]
    result = LatentTrajectoryPredictor(
        history_length=3, components=2, train_fraction=0.5
    ).evaluate(records)
    assert result.samples > 0
    assert result.beats_zero


def test_nonconsecutive_ticks_are_rejected():
    records = [record(i * 2, float(i)) for i in range(20)]
    result = LatentTrajectoryPredictor(history_length=3, components=2).evaluate(records)
    assert result.samples == 0


def test_invalid_components_are_rejected():
    with pytest.raises(ValueError):
        LatentTrajectoryPredictor(components=194)


def test_latent_encoding_is_finite():
    records = [record(i, float(np.sin(i))) for i in range(20)]
    result = LatentTrajectoryPredictor(
        history_length=2, components=2
    ).evaluate(records)
    assert np.isfinite(result.trajectory_mae)
