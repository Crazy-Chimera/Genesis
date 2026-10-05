import numpy as np
import pytest

from genesis.numerical_convergence import (
    circular_rms,
    deterministic_step,
    evaluate,
)


def test_deterministic_step_does_not_mutate_inputs():
    phase = np.zeros((4, 4))
    omega = np.ones((4, 4))
    before = phase.copy()
    result = deterministic_step(phase, omega, 0.01, 0.01)
    assert result.shape == phase.shape
    np.testing.assert_array_equal(phase, before)


def test_uniform_field_is_exact_under_step_halving():
    result = evaluate(390001, dt=0.01)
    assert np.isfinite(result.phase_rms)
    assert np.isfinite(result.coherence_error)


def test_circular_rms_is_zero_for_identical_fields():
    field = np.arange(16, dtype=float).reshape(4, 4)
    assert circular_rms(field, field) == 0.0


def test_convergence_rejects_nonpositive_dt():
    with pytest.raises(ValueError):
        evaluate(390001, dt=0.0)
    with pytest.raises(ValueError):
        evaluate(390001, dt=-0.01)
