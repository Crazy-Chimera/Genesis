import numpy as np
import pytest

from genesis.core import GenesisConfig, GenesisUniverse
from genesis.memory import TemporalMemory
from genesis.observer import LocalStructureObserver, RegionTracker
from genesis.cross_seed_generalization import CrossSeedGeneralizationPredictor


def test_cross_seed_generalization_requires_unseen_target():
    with pytest.raises(ValueError):
        CrossSeedGeneralizationPredictor().evaluate({1: [], 2: []}, [1, 2], 2)


def test_cross_seed_generalization_rejects_missing_seed():
    with pytest.raises(ValueError):
        CrossSeedGeneralizationPredictor().evaluate({1: []}, [1], 2)


def _collect(seed: int, ticks: int = 20):
    universe = GenesisUniverse(GenesisConfig(seed=seed, ticks=ticks))
    tracker = RegionTracker(LocalStructureObserver())
    memory = TemporalMemory()
    observations, events = tracker.observe_events(universe.phase)
    memory.record(universe.tick, observations, events)
    for _ in range(ticks):
        universe.step()
        observations, events = tracker.observe_events(universe.phase)
        memory.record(universe.tick, observations, events)
    return memory.all()


def test_cross_seed_generalization_returns_metrics():
    records = {1: _collect(390001), 2: _collect(390002), 3: _collect(390003)}
    result = CrossSeedGeneralizationPredictor(history_length=2).evaluate(records, [1, 2], 3)
    assert result.samples >= 0
    assert np.isfinite(result.zero_mae)
    assert np.isfinite(result.pooled_mae)
    assert np.isfinite(result.shuffled_mae)
