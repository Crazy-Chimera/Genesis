import numpy as np
import pytest

from genesis.rule_transition import (
    RuleTransitionPredictor,
    rule_transition_features,
)


def test_rule_transition_features_zero_for_identical_phase():
    phase = np.zeros((4, 4))
    omega = np.ones((4, 4))
    features = rule_transition_features(phase, phase, omega, 0.01)
    assert len(features) == 15
    assert np.allclose(features, 0.0)


def test_rule_transition_predictor_rejects_negative_ridge():
    with pytest.raises(ValueError):
        RuleTransitionPredictor(ridge=-1.0)


def test_rule_transition_predictor_empty_result():
    result = RuleTransitionPredictor().fit_predict([], [])
    assert result.samples == 0
    assert result.zero_mae == 0.0
