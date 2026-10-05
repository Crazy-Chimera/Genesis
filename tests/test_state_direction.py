from genesis.state_direction import StateDirectionPredictor


def test_direction_predictor_synthetic_relation():
    from genesis.memory import MemoryRecord

    def record(tick, value):
        return MemoryRecord(
            tick=tick, identity=1, cells=(), coherence=value,
            boundary_contrast=0.0, lifetime=1, persistence=1.0, overlap=1.0,
            local_patch=(float(value),), phase_patch=(float(value),),
            gradient_patch=(0.0,), motion=(0.0,), boundary_flux=(0.0,),
            spatial_field=(float(value),), multiscale_field=(float(value),),
            relational=(0.0,), graph_relational=(0.0,),
        )

    records = [record(i, 0.1 if i % 2 else 0.0) for i in range(20)]
    result = StateDirectionPredictor(feature_name="local_patch").evaluate(records)
    assert result.samples > 0


def test_direction_predictor_rejects_bad_config():
    import pytest
    with pytest.raises(ValueError):
        StateDirectionPredictor(train_fraction=0.0)
    with pytest.raises(ValueError):
        StateDirectionPredictor(ridge=-1.0)
    with pytest.raises(ValueError):
        StateDirectionPredictor(feature_name="missing")
