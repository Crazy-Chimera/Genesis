def test_state_delta_imports_and_validates():
    from genesis.state_delta import StateDeltaPredictor
    try:
        StateDeltaPredictor(history_length=1)
    except ValueError:
        pass
    else:
        raise AssertionError("history_length=1 must fail")

def test_state_delta_synthetic_signal():
    from genesis.memory import MemoryRecord
    from genesis.state_delta import StateDeltaPredictor
    records=[]
    for tick in range(12):
        v=float(tick)
        records.append(MemoryRecord(tick=tick,identity=1,cells=frozenset({0}),
            coherence=0.01*tick,boundary_contrast=0.0,lifetime=tick,persistence=1.0,overlap=1.0,
            local_patch=(v,)*9,phase_patch=(v,)*18,gradient_patch=(v,)*18,motion=(v,)*3,
            boundary_flux=(v,)*5,boundary_deformation=(v,)*7,spatiotemporal_patch=(v,)*36,
            spatial_field=(v,)*18,multiscale_field=(v,)*68,relational=(v,)*16,graph_relational=(v,)*33))
    r=StateDeltaPredictor(feature_name="local_patch",history_length=2,train_fraction=0.5).evaluate(records)
    assert r.samples > 0
