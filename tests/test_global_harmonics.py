import numpy as np
import pytest

from genesis.global_harmonics import global_phase_harmonics


def test_global_harmonics_excludes_first_harmonic():
    phase = np.arange(16, dtype=float).reshape(4, 4)
    values = global_phase_harmonics(phase)
    assert len(values) == 9
    assert np.all(np.isfinite(values))


def test_global_harmonics_is_bounded():
    phase = np.zeros((4, 4))
    values = global_phase_harmonics(phase)
    assert all(-1.0 <= value <= 1.0 for value in values)


def test_first_harmonic_order_is_rejected():
    with pytest.raises(ValueError):
        global_phase_harmonics(np.zeros((2, 2)), orders=(1, 2))
