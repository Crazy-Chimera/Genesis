import numpy as np
import pytest

from genesis.nonlinear import NonlinearStateInnovationPredictor


def test_nonlinear_predictor_validates_configuration():
    with pytest.raises(ValueError):
        NonlinearStateInnovationPredictor(random_features=0)
    with pytest.raises(ValueError):
        NonlinearStateInnovationPredictor(bandwidth=0)


def test_nonlinear_predictor_deterministic_transform():
    predictor = NonlinearStateInnovationPredictor(random_features=8, seed=213001)
    values = np.arange(12, dtype=float).reshape(3, 4)
    predictor._mean = values.mean(0)
    predictor._scale = values.std(0)
    predictor._scale[predictor._scale == 0] = 1
    rng = np.random.default_rng(213001)
    projection = rng.normal(size=(4, 8))
    phase = rng.uniform(0, 2 * np.pi, 8)
    first = predictor._transform(values, projection, phase)
    second = predictor._transform(values, projection, phase)
    assert np.allclose(first, second)
    assert first.shape == (3, 8)
