from genesis.state_delta import StateDeltaPredictor


def test_invalid_history():
    try:
        StateDeltaPredictor(history_length=1)
    except ValueError:
        return
    raise AssertionError("history_length=1 must fail")


def test_invalid_feature():
    try:
        StateDeltaPredictor(feature_name="missing")
    except ValueError:
        return
    raise AssertionError("unknown feature must fail")


def test_empty_records():
    result = StateDeltaPredictor().evaluate([])
    assert result.samples == 0


def test_nonconsecutive_records_produce_no_samples():
    from genesis.memory import MemoryRecord

    records = [
        MemoryRecord(
            tick=0, identity=1, cells=frozenset({0}), coherence=0.5,
            boundary_contrast=0.0, lifetime=1, persistence=1.0, overlap=0.0,
            local_patch=(0.0,) * 9, phase_patch=(0.0,) * 18,
            gradient_patch=(0.0,) * 18, motion=(0.0,) * 3,
            boundary_flux=(0.0,) * 5, boundary_deformation=(0.0,) * 7,
            spatiotemporal_patch=(0.0,) * 36, spatial_field=(0.0,) * 18,
            multiscale_field=(0.0,) * 68, relational=(0.0,) * 16,
            graph_relational=(0.0,) * 33,
        ),
        MemoryRecord(
            tick=2, identity=1, cells=frozenset({0}), coherence=0.6,
            boundary_contrast=0.0, lifetime=2, persistence=1.0, overlap=1.0,
            local_patch=(0.0,) * 9, phase_patch=(0.0,) * 18,
            gradient_patch=(0.0,) * 18, motion=(0.0,) * 3,
            boundary_flux=(0.0,) * 5, boundary_deformation=(0.0,) * 7,
            spatiotemporal_patch=(0.0,) * 36, spatial_field=(0.0,) * 18,
            multiscale_field=(0.0,) * 68, relational=(0.0,) * 16,
            graph_relational=(0.0,) * 33,
        ),
        MemoryRecord(
            tick=3, identity=1, cells=frozenset({0}), coherence=0.7,
            boundary_contrast=0.0, lifetime=3, persistence=1.0, overlap=1.0,
            local_patch=(0.0,) * 9, phase_patch=(0.0,) * 18,
            gradient_patch=(0.0,) * 18, motion=(0.0,) * 3,
            boundary_flux=(0.0,) * 5, boundary_deformation=(0.0,) * 7,
            spatiotemporal_patch=(0.0,) * 36, spatial_field=(0.0,) * 18,
            multiscale_field=(0.0,) * 68, relational=(0.0,) * 16,
            graph_relational=(0.0,) * 33,
        ),
    ]
    result = StateDeltaPredictor(history_length=2).evaluate(records)
    assert result.samples == 0
