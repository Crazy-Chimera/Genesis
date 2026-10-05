from genesis.state_change_trajectory import StateChangeTrajectoryPredictor


def test_state_change_trajectory_beats_zero_on_synthetic_signal():
    from genesis.memory import MemoryRecord

    records = []
    for tick in range(8):
        state = tuple(float(tick + offset) for offset in range(5))
        records.append(
            MemoryRecord(
                tick=tick,
                identity=1,
                cells=((0, 0),),
                coherence=0.1 * tick,
                boundary_contrast=0.0,
                lifetime=tick,
                persistence=tick,
                overlap=1.0,
                local_patch=state + (0.0, 0.0, 0.0, 0.0),
                phase_patch=state + (0.0,) * 13,
                gradient_patch=state + (0.0,) * 13,
                motion=(0.0, 0.0, 0.0),
                boundary_flux=(0.0,) * 5,
                boundary_deformation=(0.0,) * 7,
                spatiotemporal_patch=(0.0,) * 36,
                spatial_field=(0.0,) * 18,
                multiscale_field=(0.0,) * 68,
                relational=(0.0,) * 16,
                graph_relational=(0.0,) * 33,
            )
        )
    result = StateChangeTrajectoryPredictor(
        feature_name="combined", history_length=2, ridge=1e-6
    ).evaluate(records)
    assert result.samples > 0
    assert result.beats_zero


def test_state_change_trajectory_requires_consecutive_ticks():
    from genesis.memory import MemoryRecord

    base = dict(
        identity=1,
        cells=((0, 0),),
        boundary_contrast=0.0,
        lifetime=1,
        persistence=1,
        overlap=1.0,
        local_patch=(0.0,) * 9,
        phase_patch=(0.0,) * 18,
        gradient_patch=(0.0,) * 18,
        motion=(0.0,) * 3,
        boundary_flux=(0.0,) * 5,
        boundary_deformation=(0.0,) * 7,
        spatiotemporal_patch=(0.0,) * 36,
        spatial_field=(0.0,) * 18,
        multiscale_field=(0.0,) * 68,
        relational=(0.0,) * 16,
        graph_relational=(0.0,) * 33,
    )
    records = [
        MemoryRecord(tick=0, coherence=0.1, **base),
        MemoryRecord(tick=2, coherence=0.2, **base),
        MemoryRecord(tick=4, coherence=0.3, **base),
    ]
    result = StateChangeTrajectoryPredictor(
        feature_name="combined", history_length=2
    ).evaluate(records)
    assert result.samples == 0
