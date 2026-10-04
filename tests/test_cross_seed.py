from __future__ import annotations

import pytest

from genesis.cross_seed import CrossSeedTrajectoryPredictor
from genesis.memory import MemoryRecord


def rec(t: int, coherence: float, value: float) -> MemoryRecord:
    return MemoryRecord(
        tick=t,
        identity=1,
        cells=((0, 0),),
        coherence=coherence,
        boundary_contrast=0.0,
        lifetime=t + 1,
        persistence=t + 1,
        overlap=1.0,
        local_patch=(value,) + (0.0,) * 8,
        phase_patch=(value,) + (0.0,) * 17,
        gradient_patch=(value,) + (0.0,) * 17,
        motion=(value, 0.0, 0.0),
        boundary_flux=(value,) + (0.0,) * 4,
        spatial_field=(value,) + (0.0,) * 17,
        multiscale_field=(value,) + (0.0,) * 67,
        relational=(value,) + (0.0,) * 15,
        graph_relational=(value,) + (0.0,) * 32,
    )


def test_cross_seed_transfer_reconstructs_shared_signal():
    train = [rec(t, 0.1 + 0.001 * t, float(t)) for t in range(80)]
    test = [rec(t, 0.2 + 0.001 * t, float(t)) for t in range(80)]
    result = CrossSeedTrajectoryPredictor(history_length=2).evaluate(
        train, test, train_seed=1, test_seed=2
    )
    assert result.samples > 0
    assert result.transfer_mae < result.zero_mae


def test_cross_seed_requires_nonempty_and_consecutive_data():
    predictor = CrossSeedTrajectoryPredictor(history_length=2)
    assert predictor.evaluate([], []).samples == 0

    train = [rec(t, 0.1, float(t)) for t in (0, 1, 3, 4, 6, 7)]
    test = [rec(t, 0.1, float(t)) for t in (0, 1, 3, 4, 6, 7)]
    assert predictor.evaluate(train, test).samples == 0


def test_cross_seed_rejects_invalid_configuration():
    with pytest.raises(ValueError):
        CrossSeedTrajectoryPredictor(history_length=1)
    with pytest.raises(ValueError):
        CrossSeedTrajectoryPredictor(train_fraction=1.0)
    with pytest.raises(ValueError):
        CrossSeedTrajectoryPredictor(ridge=-1.0)
