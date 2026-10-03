import pytest

from genesis.local_motion import MotionPredictor
from genesis.memory import MemoryRecord


def record(tick: int, coherence: float, motion: tuple[float, float, float]) -> MemoryRecord:
    return MemoryRecord(
        tick=tick, identity=1, cells=((0, 0),), coherence=coherence,
        boundary_contrast=0.1, lifetime=tick + 1, persistence=tick + 1,
        overlap=1.0, motion=motion,
    )


def test_motion_predictor_beats_baseline_on_linear_relation():
    records = [record(t, 0.2 + 0.01 * t, (float(t), 0.0, 0.0)) for t in range(81)]
    result = MotionPredictor().evaluate(records)
    assert result.samples > 0
    assert result.motion_mae < result.baseline_mae


def test_motion_predictor_requires_exact_width():
    records = [record(t, 0.1, (0.1, 0.2, 0.3)) for t in range(1, 10)]
    bad = [
        MemoryRecord(
            tick=x.tick, identity=x.identity, cells=x.cells, coherence=x.coherence,
            boundary_contrast=x.boundary_contrast, lifetime=x.lifetime,
            persistence=x.persistence, overlap=x.overlap, motion=(0.1, 0.2),
        ) for x in records
    ]
    assert MotionPredictor().evaluate(bad).samples == 0


def test_motion_predictor_rejects_invalid_configuration():
    with pytest.raises(ValueError):
        MotionPredictor(train_fraction=0.0)
    with pytest.raises(ValueError):
        MotionPredictor(ridge=-1.0)
