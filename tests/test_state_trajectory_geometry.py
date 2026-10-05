from __future__ import annotations

from dataclasses import replace

import numpy as np
import pytest

from genesis.state_innovation import STATE_FEATURES_WITH_COMBINED, StateFeatureSpec
from genesis.state_trajectory_geometry import (
    StateTrajectoryGeometryPredictor,
    trajectory_geometry,
)


def test_geometry_is_finite_and_compact() -> None:
    spec = StateFeatureSpec("synthetic", lambda r: (float(r.tick), 1.0, 2.0), 3)
    records = [
        replace(_record(0), tick=0),
        replace(_record(1), tick=1),
        replace(_record(2), tick=2),
    ]
    values = trajectory_geometry(records, spec)
    assert len(values) == 11
    assert np.isfinite(values).all()


def test_predictor_rejects_invalid_history() -> None:
    with pytest.raises(ValueError):
        StateTrajectoryGeometryPredictor(history_length=1)


def test_predictor_rejects_unknown_feature() -> None:
    with pytest.raises(ValueError):
        StateTrajectoryGeometryPredictor(feature_name="missing")


def test_predictor_beats_zero_on_synthetic_geometry_relation() -> None:
    feature = lambda r: (float(r.tick), float(r.tick * r.tick), 1.0)
    spec = StateFeatureSpec("synthetic", feature, 3)
    records = []
    for tick in range(40):
        record = _record(tick)
        coherence = 0.01 * tick + 0.0005 * tick * tick
        records.append(replace(record, coherence=coherence))

    predictor = StateTrajectoryGeometryPredictor(
        feature_name="combined",
        history_length=3,
    )
    predictor.spec = spec
    result = predictor.evaluate(records)
    assert result.samples > 0
    assert result.beats_zero


def _record(tick: int):
    from genesis.memory import MemoryRecord

    return MemoryRecord(
        tick=tick,
        identity=1,
        cells=((0, 0),),
        coherence=0.0,
        boundary_contrast=0.0,
        lifetime=1,
        persistence=1.0,
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
        event_kinds=(),
    )
