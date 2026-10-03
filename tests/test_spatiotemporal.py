import pytest
from genesis.memory import MemoryRecord
from genesis.spatiotemporal import SpatiotemporalPredictor

def rec(t, y, patch):
    return MemoryRecord(tick=t, identity=1, cells=((0,0),), coherence=y,
        boundary_contrast=0, lifetime=t+1, persistence=t+1, overlap=1,
        spatiotemporal_patch=patch)

def test_spatiotemporal_predictor_beats_baseline_on_linear_relation():
    records=[rec(t,0.2+0.01*t,tuple([float(t)]+[0.0]*35)) for t in range(81)]
    result=SpatiotemporalPredictor().evaluate(records)
    assert result.samples > 0
    assert result.patch_mae < result.baseline_mae

def test_spatiotemporal_predictor_requires_exact_width():
    records=[rec(t,0.1,(0.1,)*35) for t in range(1,10)]
    assert SpatiotemporalPredictor().evaluate(records).samples == 0

def test_spatiotemporal_predictor_rejects_invalid_configuration():
    with pytest.raises(ValueError):
        SpatiotemporalPredictor(train_fraction=0)
    with pytest.raises(ValueError):
        SpatiotemporalPredictor(ridge=-1)
