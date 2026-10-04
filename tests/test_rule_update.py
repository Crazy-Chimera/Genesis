import numpy as np
import pytest

from genesis.rule_update import RuleUpdatePredictor, rule_update_features


def test_rule_update_features_are_finite_and_coherence_free():
    phase = np.zeros((4, 4))
    omega = np.ones((4, 4))
    values = rule_update_features(phase, omega, 0.01)
    assert len(values) == 8
    assert all(np.isfinite(values))


def test_rule_update_features_do_not_mutate_inputs():
    phase = np.arange(16, dtype=float).reshape(4, 4)
    omega = np.ones((4, 4))
    phase_before = phase.copy()
    omega_before = omega.copy()
    rule_update_features(phase, omega, 0.01)
    assert np.array_equal(phase, phase_before)
    assert np.array_equal(omega, omega_before)


def test_rule_update_predictor_rejects_negative_ridge():
    with pytest.raises(ValueError):
        RuleUpdatePredictor(ridge=-1)


def test_rule_update_predictor_empty_is_safe():
    result = RuleUpdatePredictor().fit_predict([], [])
    assert result.samples == 0
