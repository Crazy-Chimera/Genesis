import pytest
from genesis.memory import MemoryRecord
from genesis.trajectory import LocalTrajectoryPredictor

def rec(t,y,x):
    return MemoryRecord(tick=t,identity=1,cells=((0,0),),coherence=y,boundary_contrast=0,
        lifetime=t+1,persistence=t+1,overlap=1,spatial_field=x)

def test_trajectory_predictor_beats_baseline_on_linear_relation():
    rows=[tuple([float(t)]+[0.0]*17) for t in range(81)]
    r=LocalTrajectoryPredictor(history_length=3).evaluate([rec(t,0.2+0.01*t,x) for t,x in enumerate(rows)])
    assert r.samples>0 and r.trajectory_mae<r.baseline_mae

def test_trajectory_requires_consecutive_history():
    rows=[(0.0,)*18]*10
    records=[rec(t,0.1,x) for t,x in zip((0,1,3,4,6,7,9,10,12,13),rows)]
    assert LocalTrajectoryPredictor(history_length=3).evaluate(records).samples==0

def test_trajectory_rejects_invalid_configuration():
    with pytest.raises(ValueError): LocalTrajectoryPredictor(history_length=1)
    with pytest.raises(ValueError): LocalTrajectoryPredictor(ridge=-1)
