from __future__ import annotations

import numpy as np
import pytest

from genesis.core import GenesisConfig, GenesisUniverse
from genesis.mechanistic_horizon import (
    MechanisticHorizonResult,
    deterministic_next_phase,
    evaluate_horizon,
)


def test_deterministic_step_matches_noise_free_rule():
    universe = GenesisUniverse(GenesisConfig(seed=390001, ticks=1))
    expected = deterministic_next_phase(universe, universe.phase)
    assert expected.shape == universe.phase.shape
    assert np.all(np.isfinite(expected))


def test_horizon_one_is_predictive_on_small_run():
    universe = GenesisUniverse(GenesisConfig(seed=390001, ticks=10))
    result = evaluate_horizon(universe, 1)
    assert isinstance(result, MechanisticHorizonResult)
    assert result.samples == 10
    assert result.mechanistic_mae < result.zero_mae


def test_invalid_horizon():
    universe = GenesisUniverse(GenesisConfig(seed=390001, ticks=1))
    with pytest.raises(ValueError):
        evaluate_horizon(universe, 0)
