import numpy as np
import pytest

from genesis.global_phase import GlobalPhasePredictor, phase_features


def record(tick, phase, coherence):
    return (tick, np.asarray(phase, dtype=float), coherence)


def test_phase_features_are_sincos_and_fixed_width():
    values = np.zeros((2, 2))
    features = phase_features(values)
    assert len(features) == 8
    assert features[:4] == (0.0, 0.0, 0.0, 0.0)
    assert features[4:] == (1.0, 1.0, 1.0, 1.0)


def test_global_phase_reconstructs_synthetic_innovation():
    records = [
        record(t, np.full((2, 2), float(t)), 0.1 + 0.0001 * t * t)
        for t in range(40)
    ]
    result = GlobalPhasePredictor(ridge=1e-6).evaluate(records)
    assert result.samples > 0
    assert result.beats_zero
    assert result.beats_shuffled


def test_global_phase_requires_consecutive_ticks():
    records = [
        record(t, np.zeros((2, 2)), 0.1 + 0.001 * t)
        for t in (0, 2, 4, 6, 8)
    ]
    assert GlobalPhasePredictor().evaluate(records).samples == 0


def test_global_phase_rejects_invalid_configuration():
    with pytest.raises(ValueError):
        GlobalPhasePredictor(train_fraction=0.0)
    with pytest.raises(ValueError):
        GlobalPhasePredictor(ridge=-1.0)
