import numpy as np
from genesis.memory import MemoryRecord
from genesis.state_delta import StateDeltaPredictor

def record(tick, value):
    return MemoryRecord(
        tick=tick, identity=1, cells=((0,0),), coherence=value,
        boundary_contrast=0.0, lifetime=tick+1, persistence=tick+1,
        overlap=1.0, local_patch=(value,)*9, phase_patch=(value,)*18,
        gradient_patch=(value,)*18, motion=(0.0,0.0,0.0),
        boundary_flux=(value,)*5, boundary_deformation=(value,)*5,
        spatiotemporal_patch=(value,)*36, spatial_field=(value,)*18,
        multiscale_field=(value,)*68, relational=(value,)*16,
        graph_relational=(value,)*33,
    )

def test_delta_predictor_validates_history():
    try:
        StateDeltaPredictor(history_length=1)
    except ValueError:
        return
    assert False

def test_delta_predictor_requires_consecutive_ticks():
    records = [record(0,0.0), record(2,0.1), record(3,0.2)]
    result = StateDeltaPredictor(history_length=2).evaluate(records)
    assert result.samples == 0

def test_delta_predictor_finite_result():
    records = [record(i, i*0.01) for i in range(12)]
    result = StateDeltaPredictor(history_length=3).evaluate(records)
    assert result.samples > 0
    assert np.isfinite(result.delta_mae)
