from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pytest

from genesis.memory import MemoryRecord
from genesis.state_derivative import StateDerivativePredictor


def record(tick: int, value: float, coherence: float) -> MemoryRecord:
    return MemoryRecord(
        tick=tick,
        identity=1,
        coherence=coherence,
        cells=(0,),
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


def test_derivative_predictor_can_recover_synthetic_change():
    records = [
        record(tick, float(tick), 0.1 + 0.01 * tick)
        for tick in range(1, 20)
    ]
    result = StateDerivativePredictor(
        feature_name="combined",
        train_fraction=0.5,
        ridge=1e-6,
    ).evaluate(records)
    assert result.samples > 0
    assert result.beats_zero


def test_derivative_predictor_requires_consecutive_ticks():
    records = [record(0, 0.0, 0.1), record(2, 2.0, 0.2)]
    result = StateDerivativePredictor().evaluate(records)
    assert result.samples == 0


def test_derivative_predictor_rejects_invalid_configuration():
    with pytest.raises(ValueError):
        StateDerivativePredictor(train_fraction=0.0)
    with pytest.raises(ValueError):
        StateDerivativePredictor(ridge=-1.0)
    with pytest.raises(ValueError):
        StateDerivativePredictor(feature_name="missing")
