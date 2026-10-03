import pytest

from genesis.boundary_flux import BoundaryFluxPredictor
from genesis.memory import MemoryRecord


def record(tick: int, coherence: float, flux: tuple[float, ...]) -> MemoryRecord:
    return MemoryRecord(
        tick=tick, identity=1, cells=((0, 0),), coherence=coherence,
        boundary_contrast=0.1, lifetime=tick + 1, persistence=tick + 1,
        overlap=1.0, boundary_flux=flux,
    )


def test_boundary_flux_predictor_beats_baseline_on_linear_relation():
    records = [record(t, 0.2 + 0.01 * t, (float(t), 0.0, 0.0, 1.0, 1.0)) for t in range(81)]
    result = BoundaryFluxPredictor().evaluate(records)
    assert result.samples > 0
    assert result.flux_mae < result.baseline_mae


def test_boundary_flux_predictor_requires_exact_width():
    records = [record(t, 0.1, (0.1, 0.2, 0.3, 4.0, 1.0)) for t in range(1, 10)]
    bad = [
        MemoryRecord(
            tick=x.tick, identity=x.identity, cells=x.cells, coherence=x.coherence,
            boundary_contrast=x.boundary_contrast, lifetime=x.lifetime,
            persistence=x.persistence, overlap=x.overlap, boundary_flux=(0.1, 0.2),
        ) for x in records
    ]
    assert BoundaryFluxPredictor().evaluate(bad).samples == 0


def test_boundary_flux_predictor_rejects_invalid_configuration():
    with pytest.raises(ValueError):
        BoundaryFluxPredictor(train_fraction=0.0)
    with pytest.raises(ValueError):
        BoundaryFluxPredictor(ridge=-1.0)
