from __future__ import annotations

import pytest

from genesis.memory import MemoryRecord
from genesis.state_delta import StateDeltaPredictor


def make_record(tick: int, value: float, coherence: float) -> MemoryRecord:
    return MemoryRecord(
        tick=tick,
        identity=1,
        cells=((0, 0),),
        coherence=coherence,
        boundary_contrast=0.0,
        lifetime=tick,
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


def test_delta_predictor_beats_zero_on_synthetic_relation():
    records = []
    for tick in range(1, 21):
        value = float(tick * tick)
        coherence = 0.0005 * tick * tick
        records.append(make_record(tick, value, coherence))

    result = StateDeltaPredictor(
        history_length=3,
        train_fraction=0.5,
        ridge=1e-8,
        require_consecutive=True,
    ).evaluate(records)

    assert result.samples > 0
    assert result.delta_mae < result.zero_mae
    assert result.delta_mae < result.shuffled_mae


def test_delta_predictor_skips_nonconsecutive_history():
    records = [make_record(tick, float(tick), 0.01 * tick)
               for tick in (1, 2, 4, 5, 7, 8)]
    result = StateDeltaPredictor(history_length=3).evaluate(records)
    assert result.samples == 0


@pytest.mark.parametrize(
    "kwargs",
    [
        {"history_length": 1},
        {"train_fraction": 0.0},
        {"train_fraction": 1.0},
        {"ridge": -1.0},
        {"feature_name": "missing"},
    ],
)
def test_delta_predictor_rejects_invalid_configuration(kwargs):
    with pytest.raises(ValueError):
        StateDeltaPredictor(**kwargs)
