from __future__ import annotations

import pytest

from genesis.memory import MemoryRecord
from genesis.state_velocity import StateVelocityPredictor


def make_record(tick: int, value: float) -> MemoryRecord:
    return MemoryRecord(
        tick=tick,
        identity=1,
        cells=((0, 0),),
        coherence=value,
        boundary_contrast=0.0,
        lifetime=tick + 1,
        persistence=1.0,
        overlap=1.0,
        event_kinds=(),
        local_patch=(value,) * 9,
        phase_patch=(value,) * 18,
        gradient_patch=(value,) * 18,
        motion=(value,) * 3,
        boundary_flux=(value,) * 5,
        spatiotemporal_patch=(value,) * 36,
        spatial_field=(value,) * 18,
        multiscale_field=(value,) * 68,
        relational=(value,) * 16,
        graph_relational=(value,) * 33,
    )


def test_velocity_predictor_validates_config() -> None:
    with pytest.raises(ValueError):
        StateVelocityPredictor(train_fraction=0.0)
    with pytest.raises(ValueError):
        StateVelocityPredictor(train_fraction=1.0)
    with pytest.raises(ValueError):
        StateVelocityPredictor(ridge=-1.0)


def test_velocity_predictor_requires_consecutive_ticks() -> None:
    records = [make_record(0, 0.0), make_record(2, 1.0)]
    result = StateVelocityPredictor().evaluate(records)
    assert result.samples == 0


def test_velocity_predictor_returns_result_for_consecutive_records() -> None:
    records = [make_record(i, float(i)) for i in range(8)]
    result = StateVelocityPredictor().evaluate(records)
    assert result.samples > 0
    assert result.heldout_start_tick > 0
