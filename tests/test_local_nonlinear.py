from genesis.local_nonlinear import NonlinearLocalPatchPredictor
from genesis.memory import MemoryRecord


def record(tick: int, coherence: float, x: float) -> MemoryRecord:
    patch = (x,) * 9
    return MemoryRecord(
        tick=tick,
        identity=1,
        cells=((0, 0),),
        coherence=coherence,
        boundary_contrast=0.1,
        lifetime=tick + 1,
        persistence=tick + 1,
        overlap=1.0,
        local_patch=patch,
    )


def test_nonlinear_predictor_beats_baseline_on_quadratic_relation():
    # At tick t the local patch is x=t and the next coherence is a
    # quadratic function of the previous patch: f(x) = 0.2 + 0.00005*(x+1)^2.
    records = [
        record(t, 0.2 + 0.00005 * t**2, float(t))
        for t in range(81)
    ]
    result = NonlinearLocalPatchPredictor().evaluate(records)
    assert result.samples > 0
    assert result.nonlinear_mae < result.baseline_mae


def test_nonlinear_predictor_requires_exact_patch_width():
    records = [record(t, 0.1, 0.1) for t in range(1, 10)]
    records = [
        MemoryRecord(
            tick=item.tick,
            identity=item.identity,
            cells=item.cells,
            coherence=item.coherence,
            boundary_contrast=item.boundary_contrast,
            lifetime=item.lifetime,
            persistence=item.persistence,
            overlap=item.overlap,
            local_patch=(0.1,) * 8,
        )
        for item in records
    ]
    result = NonlinearLocalPatchPredictor().evaluate(records)
    assert result.samples == 0
def test_nonlinear_predictor_rejects_invalid_configuration():
    import pytest

    with pytest.raises(ValueError):
        NonlinearLocalPatchPredictor(train_fraction=0.0)
    with pytest.raises(ValueError):
        NonlinearLocalPatchPredictor(ridge=-1.0)
    with pytest.raises(ValueError):
        NonlinearLocalPatchPredictor(radius=-1)
