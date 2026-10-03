import pytest
from genesis.memory import MemoryRecord
from genesis.spatial_field import SpatialFieldPredictor
def rec(t,y,f):
    return MemoryRecord(tick=t,identity=1,cells=((0,0),),coherence=y,boundary_contrast=0,lifetime=t+1,persistence=t+1,overlap=1,spatial_field=f)
def test_spatial_field_predictor():
    r=[rec(t,.2+.01*t,tuple([float(t)]+[0.]*17)) for t in range(81)]
    x=SpatialFieldPredictor().evaluate(r); assert x.samples>0 and x.field_mae<x.baseline_mae
def test_spatial_field_width():
    r=[rec(t,.1,(.1,)*17) for t in range(1,10)]
    assert SpatialFieldPredictor().evaluate(r).samples==0
def test_invalid():
    with pytest.raises(ValueError): SpatialFieldPredictor(train_fraction=0)
    with pytest.raises(ValueError): SpatialFieldPredictor(ridge=-1)
