from __future__ import annotations

import numpy as np
import pytest

from genesis.memory import MemoryRecord
from genesis.state_increment import StateIncrementPredictor


def record(tick: int, value: float, coherence: float) -> MemoryRecord:
    return MemoryRecord(
        tick=tick,
        identity=1,
        cells=((0, 0),),
        coherence=coherence,
        boundary_contrast=0.0,
        lifetime=tick + 1,
        persistence=tick + 1,
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


def test_increment_predictor_rejects_invalid_history():
    with pytest.raises(ValueError):
        StateIncrementPredictor(history_length=1)


def test_increment_predictor_requires_consecutive_ticks():
    records = [record(0, 0.0, 0.0), record(1, 1.0, 0.1), record(3, 3.0, 0.2)]
    result = StateIncrementPredictor(history_length=2).evaluate(records)
    assert result.samples == 0


def test_increment_predictor_can_capture_synthetic_increment_signal():
    records = [
        record(tick, float(tick), 0.01 * tick + 0.001 * tick * tick)
        for tick in range(20)
    ]
    result = StateIncrementPredictor(
        feature_name="structure",
        history_length=2,
        train_fraction=0.5,
    ).evaluate(records)
    assert result.samples > 0
    assert np.isfinite(result.increment_mae)
    assert result.increment_mae < result.zero_mae
