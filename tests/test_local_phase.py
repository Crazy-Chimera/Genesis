from genesis.local_phase import PhasePatchPredictor
from genesis.memory import MemoryRecord


def record(tick: int, coherence: float, x: float) -> MemoryRecord:
    patch = tuple(value for i in range(9) for value in (x, 1.0))
    return MemoryRecord(
        tick=tick,
        identity=1,
        cells=((0, 0),),
        coherence=coherence,
        boundary_contrast=0.1,
        lifetime=tick + 1,
        persistence=tick + 1,
        overlap=1.0,
        phase_patch=patch,
    )


def test_phase_predictor_beats_baseline_on_linear_relation():
    records = [record(t, 0.2 + 0.001 * t, float(t)) for t in range(81)]
    result = PhasePatchPredictor().evaluate(records)
    assert result.samples > 0
    assert result.phase_mae < result.baseline_mae


def test_phase_predictor_requires_exact_patch_width():
    records = [record(t, 0.1, 0.1) for t in range(1, 10)]
    bad = []
    for item in records:
        bad.append(
            MemoryRecord(
                tick=item.tick,
                identity=item.identity,
                cells=item.cells,
                coherence=item.coherence,
                boundary_contrast=item.boundary_contrast,
                lifetime=item.lifetime,
                persistence=item.persistence,
                overlap=item.overlap,
                phase_patch=(0.1,) * 17,
            )
        )
    assert PhasePatchPredictor().evaluate(bad).samples == 0


def test_phase_predictor_rejects_invalid_configuration():
    import pytest

    with pytest.raises(ValueError):
        PhasePatchPredictor(train_fraction=0.0)
    with pytest.raises(ValueError):
        PhasePatchPredictor(ridge=-1.0)
    with pytest.raises(ValueError):
        PhasePatchPredictor(radius=-1)
