import pytest
from genesis.memory import MemoryRecord
from genesis.multiscale import MultiscaleFieldPredictor

def rec(t,y,x):
    return MemoryRecord(tick=t,identity=1,cells=((0,0),),coherence=y,boundary_contrast=0,lifetime=t+1,persistence=t+1,overlap=1,multiscale_field=x)

def test_multiscale_predictor_beats_baseline_on_linear_relation():
    rows=[tuple([float(t)]+[0.0]*67) for t in range(81)]
    r=MultiscaleFieldPredictor().evaluate([rec(t,0.2+0.01*t,x) for t,x in enumerate(rows)])
    assert r.samples>0 and r.field_mae<r.baseline_mae

def test_multiscale_predictor_requires_width():
    assert MultiscaleFieldPredictor().evaluate([rec(t,0.1,(0.0,)*67) for t in range(1,10)]).samples==0

def test_multiscale_predictor_rejects_invalid_configuration():
    with pytest.raises(ValueError): MultiscaleFieldPredictor(train_fraction=0)
    with pytest.raises(ValueError): MultiscaleFieldPredictor(ridge=-1)
