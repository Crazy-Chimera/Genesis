import numpy as np

from genesis.core import GenesisConfig, GenesisUniverse
from genesis.mechanistic_decomposition import (
    MechanisticDecompositionEvaluator,
    rule_next_phase_frequency_only,
)


def test_frequency_only_rule_does_not_mutate_universe():
    universe = GenesisUniverse(GenesisConfig(seed=390001))
    before = universe.phase.copy()
    predicted = rule_next_phase_frequency_only(universe)
    assert predicted.shape == before.shape
    np.testing.assert_array_equal(universe.phase, before)


def test_decomposition_is_exact_without_noise():
    universe = GenesisUniverse(
        GenesisConfig(seed=390001, noise=0.0, ticks=10)
    )
    result = MechanisticDecompositionEvaluator().evaluate(universe)
    assert result.samples == 10
    assert result.full_rule_mae < 1e-14
    assert result.full_beats_frequency_only


def test_decomposition_result_is_finite():
    universe = GenesisUniverse(
        GenesisConfig(seed=390001, noise=0.001, ticks=10)
    )
    result = MechanisticDecompositionEvaluator().evaluate(universe)
    assert np.isfinite(result.zero_mae)
    assert np.isfinite(result.frequency_only_mae)
    assert np.isfinite(result.full_rule_mae)
