import numpy as np
import pytest

from genesis.core import GenesisConfig, GenesisUniverse
from genesis.rule_native import RuleNativePredictor, rule_native_features


def test_rule_native_features_are_coherence_free_and_finite():
    u = GenesisUniverse(GenesisConfig(size=4, seed=390001))
    f = rule_native_features(u.phase, u.omega)
    assert len(f) == 12
    assert np.all(np.isfinite(f))


def test_rule_native_predictor_beats_zero_on_synthetic_relation():
    train = [((float(i), 0.0) + (0.0,) * 10, 0.2 * i) for i in range(20)]
    test = [((float(i), 0.0) + (0.0,) * 10, 0.2 * i) for i in range(20, 30)]
    r = RuleNativePredictor().fit_predict(train, test)
    assert r.samples == 10
    assert r.rule_mae < r.zero_mae


def test_rule_native_rejects_negative_ridge():
    with pytest.raises(ValueError):
        RuleNativePredictor(ridge=-1)
