from __future__ import annotations

import numpy as np

from genesis.memory import MemoryRecord
from genesis.state_innovation import combined_state
from genesis.state_slope import StateSlopePredictor


def record(tick: int, value: float, coherence: float) -> MemoryRecord:
    return MemoryRecord(
        tick=tick,
        identity=1,
        cells=((0, 0),),
        coherence=coherence,
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


def test_slope_predictor_beats_zero_on_synthetic_trend() -> None:
    records = [record(i, float(i), 0.001 * i) for i in range(20)]
    result = StateSlopePredictor(history_length=3).evaluate(records)
    assert result.samples > 0
    assert result.beats_zero
    assert result.beats_shuffled


def test_slope_predictor_rejects_nonconsecutive_history() -> None:
    records = [record(i, float(i), 0.001 * i) for i in (0, 2, 4, 6, 8)]
    result = StateSlopePredictor(history_length=3).evaluate(records)
    assert result.samples == 0


def test_slope_predictor_validates_configuration() -> None:
    records = [record(i, float(i), 0.001 * i) for i in range(8)]
    for kwargs in (
        {"history_length": 1},
        {"train_fraction": 0.0},
        {"train_fraction": 1.0},
        {"ridge": -1.0},
        {"feature_name": "missing"},
    ):
        try:
            StateSlopePredictor(**kwargs)
        except ValueError:
            pass
        else:
            raise AssertionError("expected ValueError")


def test_combined_state_width_is_stable() -> None:
    item = record(0, 1.0, 0.1)
    assert len(combined_state(item)) == 193
