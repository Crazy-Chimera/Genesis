from __future__ import annotations

import pytest

from genesis.memory import MemoryRecord
from genesis.nonlinear_state import NonlinearStatePredictor


def record(tick: int, value: float) -> MemoryRecord:
    return MemoryRecord(
        tick=tick,
        identity=1,
        cells=((0, 0),),
        coherence=value,
        boundary_contrast=0.0,
        lifetime=tick,
        persistence=1,
        overlap=1.0,
        local_patch=(0.0,) * 9,
        phase_patch=(0.0,) * 18,
        gradient_patch=(0.0,) * 18,
        motion=(0.0,) * 3,
        boundary_flux=(0.0,) * 5,
        boundary_deformation=(0.0,) * 7,
        spatiotemporal_patch=(0.0,) * 36,
        spatial_field=(0.0,) * 18,
        multiscale_field=(0.0,) * 68,
        relational=(0.0,) * 16,
        graph_relational=(0.0,) * 33,
    )


def test_predictor_is_deterministic() -> None:
    records = [record(i, float(i * i) * 1e-4) for i in range(20)]
    a = NonlinearStatePredictor(feature_count=8).evaluate(records)
    b = NonlinearStatePredictor(feature_count=8).evaluate(records)
    assert a == b


def test_invalid_configuration() -> None:
    with pytest.raises(ValueError):
        NonlinearStatePredictor(feature_count=0)
    with pytest.raises(ValueError):
        NonlinearStatePredictor(ridge=-1)
    with pytest.raises(ValueError):
        NonlinearStatePredictor(train_fraction=1.0)


def test_nonconsecutive_records_can_be_excluded() -> None:
    records = [record(0, 0.1), record(2, 0.2), record(4, 0.3), record(6, 0.4)]
    result = NonlinearStatePredictor(require_consecutive=True).evaluate(records)
    assert result.samples == 0
