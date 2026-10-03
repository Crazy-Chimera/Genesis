import numpy as np
from genesis.nonlinear_state_trajectory import NonlinearStateTrajectoryPredictor
from genesis.state_innovation import StateFeatureSpec

def test_invalid_configuration():
    for kwargs in ({"history_length":1},{"train_fraction":0.0},{"train_fraction":1.0},{"ridge":-1.0},{"random_features":0},{"feature_name":"missing"}):
        try: NonlinearStateTrajectoryPredictor(**kwargs)
        except ValueError: pass
        else: raise AssertionError("invalid configuration was accepted")

def test_empty_records():
    result=NonlinearStateTrajectoryPredictor().evaluate([])
    assert result.samples==0 and result.zero_mae==0.0

def test_synthetic_nonlinear_signal_beats_zero():
    class Record:
        def __init__(self,tick,value,coherence):
            self.tick=tick; self.identity=1; self.value=value; self.coherence=coherence
    predictor=NonlinearStateTrajectoryPredictor(feature_name="synthetic",history_length=2,random_features=128,ridge=1e-3)
    predictor.spec=StateFeatureSpec("synthetic",lambda r:(r.value,),1)
    records=[]
    for tick in range(200):
        value=np.sin(tick/7.0); coherence=0.01*np.tanh(value*value)
        records.append(Record(tick,value,coherence))
    result=predictor.evaluate(records)
    assert result.beats_zero
