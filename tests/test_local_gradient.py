import numpy as np
import pytest

from genesis.local_gradient import LocalGradientPredictor
from genesis.memory import MemoryRecord


def record(tick: int, coherence: float, x: float) -> MemoryRecord:
    patch = tuple(value for _ in range(9) for value in (x, 0.0))
    return MemoryRecord(
        tick=tick,
        identity=1,
        cells=((0, 0),),
        coherence=coherence,
        boundary_contrast=0.1,
        lifetime=tick + 1,
        persistence=tick + 1,
        overlap=1.0,
        gradient_patch=patch,
    )


def test_gradient_predictor_beats_baseline_on_linear_relation():
    records = [record(t, 0.2 + 0.001 * t, float(t)) for t in range(81)]
    result = LocalGradientPredictor().evaluate(records)
    assert result.samples > 0
    assert result.gradient_mae < result.baseline_mae


def test_gradient_predictor_requires_exact_patch_width():
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
                gradient_patch=(0.1,) * 17,
            )
        )
    assert LocalGradientPredictor().evaluate(bad).samples == 0


def test_gradient_predictor_rejects_invalid_configuration():
    with pytest.raises(ValueError):
        LocalGradientPredictor(train_fraction=0.0)
    with pytest.raises(ValueError):
        LocalGradientPredictor(ridge=-1.0)
    with pytest.raises(ValueError):
        LocalGradientPredictor(radius=-1)


def test_wrapped_gradient_is_bounded():
    phase = np.array([[0.0, 3.0], [-3.0, 0.0]])
    dx = np.angle(np.exp(1j * (np.roll(phase, -1, axis=1) - phase)))
    dy = np.angle(np.exp(1j * (np.roll(phase, -1, axis=0) - phase)))
    assert np.all(dx >= -np.pi)
    assert np.all(dx <= np.pi)
    assert np.all(dy >= -np.pi)
    assert np.all(dy <= np.pi)
