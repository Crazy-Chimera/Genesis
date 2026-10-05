import numpy as np

from genesis.core import GenesisConfig, GenesisUniverse
from genesis.mechanistic import (
    MechanisticOneStepPredictor,
    rule_next_phase_without_noise,
)


def test_rule_prediction_does_not_mutate_universe():
    universe = GenesisUniverse(GenesisConfig(seed=390001))
    before = universe.phase.copy()
    predicted = rule_next_phase_without_noise(universe)
    assert predicted.shape == before.shape
    np.testing.assert_array_equal(universe.phase, before)


def test_mechanistic_predictor_beats_zero_on_deterministic_rule():
    universe = GenesisUniverse(GenesisConfig(seed=390001, noise=0.0, ticks=10))
    result = MechanisticOneStepPredictor().evaluate(universe)
    assert result.samples == 10
    assert result.mechanistic_mae < 1e-14
    assert result.beats_zero


def test_mechanistic_result_improvement():
    universe = GenesisUniverse(GenesisConfig(seed=390001, noise=0.0, ticks=1))
    result = MechanisticOneStepPredictor().evaluate(universe)
    assert result.improvement > 0.0
