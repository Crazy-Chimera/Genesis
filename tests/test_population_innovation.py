import numpy as np
import pytest

from genesis.memory import MemoryRecord
from genesis.population_innovation import (
    PopulationInnovationPredictor,
    population_state,
)


def make_record(tick: int, coherence: float, size: int) -> MemoryRecord:
    return MemoryRecord(
        tick=tick,
        identity=1,
        cells=tuple(range(size)),
        coherence=coherence,
        boundary_contrast=0.1,
        lifetime=tick + 1,
        persistence=0.5,
        overlap=0.2,
        local_patch=(0.0,) * 9,
        phase_patch=(0.0,) * 18,
        gradient_patch=(0.0,) * 18,
        motion=(0.0, 0.0, 0.0),
        boundary_flux=(0.0,) * 5,
        boundary_deformation=(0.0,) * 7,
        spatiotemporal_patch=(0.0,) * 36,
        spatial_field=(0.0,) * 18,
        multiscale_field=(0.0,) * 68,
        relational=(0.0,) * 16,
        graph_relational=(0.0,) * 33,
    )


def test_population_state_has_fixed_width():
    tick, state = population_state([make_record(4, 0.2, 3), make_record(4, 0.2, 5)])
    assert tick == 4
    assert len(state) == 12
    assert state[0] == 2
    assert state[1] == 8


def test_population_predictor_finds_synthetic_relation():
    records = []
    for tick in range(20):
        size = tick + 1
        coherence = 0.1 + 0.001 * tick + 0.0001 * tick * tick
        records.append(make_record(tick, coherence, size))
    result = PopulationInnovationPredictor(train_fraction=0.5, ridge=1e-8).evaluate(records)
    assert result.samples > 0
    assert result.beats_zero
    assert result.beats_shuffled


def test_population_predictor_requires_consecutive_ticks():
    records = [make_record(tick, 0.1 + tick * 0.01, 2) for tick in (0, 2, 4, 6)]
    result = PopulationInnovationPredictor(require_consecutive=True).evaluate(records)
    assert result.samples == 0


def test_invalid_population_predictor_config():
    with pytest.raises(ValueError):
        PopulationInnovationPredictor(train_fraction=0)
    with pytest.raises(ValueError):
        PopulationInnovationPredictor(ridge=-1)
