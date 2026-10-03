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
    records = [
        record(t, 0.2 + 0.05 * ((t - 1) % 7) ** 2, float((t - 1) % 7))
        for t in range(1, 81)
    ]
    result = NonlinearLocalPatchPredictor().evaluate(records)
    assert result.samples > 0
    assert result.nonlinear_mae < result.baseline_mae


def test_nonlinear_predictor_requires_exact_patch_width():
    records = [record(t, 0.1, 0.1) for t in range(1, 10)]
    records[0] = MemoryRecord(
        tick=records[0].tick,
        identity=records[0].identity,
        cells=records[0].cells,
        coherence=records[0].coherence,
        boundary_contrast=records[0].boundary_contrast,
        lifetime=records[0].lifetime,
        persistence=records[0].persistence,
        overlap=records[0].overlap,
        local_patch=(0.1,) * 8,
    )
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
