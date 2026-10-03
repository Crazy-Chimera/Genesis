from genesis.local import LocalPatchPredictor
from genesis.memory import MemoryRecord


def record(tick: int, coherence: float, patch: tuple[float, ...]) -> MemoryRecord:
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


def test_local_patch_predictor_beats_baseline_on_synthetic_relation():
    records = [
        record(t, 0.1 + 0.02 * ((t - 1) % 3), tuple([float((t - 1) % 3)] * 9))
        for t in range(1, 41)
    ]
    result = LocalPatchPredictor().evaluate(records)
    assert result.samples > 0
    assert result.local_mae < result.baseline_mae


def test_local_patch_predictor_requires_exact_patch_width():
    records = [record(t, 0.1, (0.1,) * 8) for t in range(10)]
    result = LocalPatchPredictor().evaluate(records)
    assert result.samples == 0


def test_local_patch_predictor_rejects_invalid_configuration():
    import pytest
    with pytest.raises(ValueError):
        LocalPatchPredictor(train_fraction=0.0)
    with pytest.raises(ValueError):
        LocalPatchPredictor(ridge=-1.0)
    with pytest.raises(ValueError):
        LocalPatchPredictor(radius=-1)
