import numpy as np

from genesis import GenesisConfig, GenesisObserver, GenesisUniverse


def test_seed_reproduces_initial_state_and_trajectory():
    cfg = GenesisConfig(ticks=5)
    a = GenesisUniverse(cfg)
    b = GenesisUniverse(cfg)

    for _ in range(cfg.ticks):
        np.testing.assert_array_equal(a.step(), b.step())


def test_local_topology_preserves_population():
    universe = GenesisUniverse(GenesisConfig(size=16))
    assert universe.config.count == 256
    assert universe.phase.shape == (16, 16)


def test_observer_does_not_change_universe_state():
    universe = GenesisUniverse(GenesisConfig())
    observer = GenesisObserver()

    before = universe.phase.copy()
    observer.measure(universe)

    np.testing.assert_array_equal(before, universe.phase)


def test_coherence_is_bounded():
    universe = GenesisUniverse(GenesisConfig())
    coherence = GenesisObserver().coherence(universe.phase)
    assert 0.0 <= coherence <= 1.0
