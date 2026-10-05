from genesis.state_direction import StateDirectionPredictor


def test_direction_predictor_synthetic_relation():
    from genesis.memory import MemoryRecord

    def record(tick, value):
        return MemoryRecord(
            tick=tick, identity=1, cells=(), coherence=value,
            boundary_contrast=0.0, lifetime=1, persistence=1, overlap=1.0,
            local_patch=(float(value),) * 9,
            phase_patch=(float(value),) * 18,
            gradient_patch=(0.0,) * 18,
            motion=(0.0,) * 3,
            boundary_flux=(0.0,) * 5,
            spatial_field=(float(value),) * 18,
            multiscale_field=(float(value),) * 68,
            relational=(0.0,) * 16,
            graph_relational=(0.0,) * 33,
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
