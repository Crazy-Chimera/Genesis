import pytest

from genesis.boundary_deformation import BoundaryDeformationPredictor
from genesis.memory import MemoryRecord


def record(tick: int, coherence: float, deformation: tuple[float, ...]) -> MemoryRecord:
    return MemoryRecord(
        tick=tick, identity=1, cells=((0, 0),), coherence=coherence,
        boundary_contrast=0.1, lifetime=tick + 1, persistence=tick + 1,
        overlap=1.0, boundary_deformation=deformation,
    )


def test_boundary_deformation_predictor_beats_baseline_on_linear_relation():
    records = [
        record(t, 0.2 + 0.01 * t, (float(t), 0.0, 0.0, 0.0, 0.0, 0.0, 0.0))
        for t in range(81)
    ]
    result = BoundaryDeformationPredictor().evaluate(records)
    assert result.samples > 0
    assert result.deformation_mae < result.baseline_mae


def test_boundary_deformation_predictor_requires_exact_width():
    records = [
        record(t, 0.1, (0.1, 0.2, 0.3, 0.4, 0.5, 0.6))
        for t in range(1, 10)
    ]
    assert BoundaryDeformationPredictor().evaluate(records).samples == 0


def test_boundary_deformation_predictor_rejects_invalid_configuration():
    with pytest.raises(ValueError):
        BoundaryDeformationPredictor(train_fraction=1.0)
    with pytest.raises(ValueError):
        BoundaryDeformationPredictor(ridge=-1.0)
