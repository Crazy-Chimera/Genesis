from __future__ import annotations

import numpy as np
import pytest

from genesis.rule_distribution import (
    RuleDistributionPredictor,
    rule_distribution_features,
)


def test_rule_distribution_features_are_finite_and_fixed_width():
    phase = np.zeros((4, 4))
    omega = np.ones((4, 4))
    features = rule_distribution_features(phase, omega, 0.01)
    assert len(features) == 15
    assert np.isfinite(features).all()


def test_rule_distribution_predictor_rejects_negative_ridge():
    with pytest.raises(ValueError):
        RuleDistributionPredictor(ridge=-1.0)


def test_rule_distribution_predictor_beats_zero_on_synthetic_relation():
    train = [((float(i),), float(i) * 0.1) for i in range(20)]
    test = [((float(i),), float(i) * 0.1) for i in range(20, 30)]
    result = RuleDistributionPredictor().fit_predict(train, test)
    assert result.beats_zero
