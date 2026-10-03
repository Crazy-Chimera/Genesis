import numpy as np
import pytest

from genesis import GenesisConfig, GenesisObserver, GenesisUniverse


def test_seed_reproduces_initial_state_and_trajectory():
    cfg = GenesisConfig(ticks=5)
    a = GenesisUniverse(cfg)
    b = GenesisUniverse(cfg)

    for _ in range(cfg.ticks):
        np.testing.assert_array_equal(a.step(), b.step())


def test_reference_pw001_final_coherence():
    universe = GenesisUniverse(GenesisConfig(ticks=100_000))
    observer = GenesisObserver()

    for _ in range(universe.config.ticks):
        universe.step()

    assert observer.coherence(universe.phase) == pytest.approx(
        0.09507548138916427, abs=1e-15
    )


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


from genesis import LocalStructureObserver


def test_local_coherence_is_bounded():
    universe = GenesisUniverse(GenesisConfig(size=4))
    local = LocalStructureObserver().local_coherence(universe.phase)
    assert local.shape == universe.phase.shape
    assert np.all((local >= 0.0) & (local <= 1.0))


def test_uniform_phase_forms_one_periodic_cluster():
    phase = np.zeros((4, 4))
    clusters = LocalStructureObserver(threshold=0.99).detect(phase)
    assert len(clusters) == 1
    assert len(clusters[0].cells) == 16
    assert clusters[0].coherence == pytest.approx(1.0)


def test_cluster_detection_is_measurement_only():
    universe = GenesisUniverse(GenesisConfig(size=4))
    observer = LocalStructureObserver()
    before = universe.phase.copy()
    observer.detect(universe.phase)
    np.testing.assert_array_equal(before, universe.phase)
