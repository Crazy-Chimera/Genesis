import numpy as np
import pytest

from genesis import (
    GenesisConfig,
    GenesisObserver,
    GenesisUniverse,
    LocalStructureObserver,
    RegionTracker,
)


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
    before = universe.phase.copy()
    GenesisObserver().measure(universe)
    np.testing.assert_array_equal(before, universe.phase)


def test_coherence_is_bounded():
    coherence = GenesisObserver().coherence(GenesisUniverse().phase)
    assert 0.0 <= coherence <= 1.0


def test_local_coherence_is_bounded():
    universe = GenesisUniverse(GenesisConfig(size=4))
    local = LocalStructureObserver().local_coherence(universe.phase)
    assert local.shape == universe.phase.shape
    assert np.all((local >= 0.0) & (local <= 1.0))


def test_uniform_phase_forms_one_periodic_cluster():
    clusters = LocalStructureObserver(threshold=0.99).detect(np.zeros((4, 4)))
    assert len(clusters) == 1
    assert len(clusters[0].cells) == 16
    assert clusters[0].coherence == pytest.approx(1.0)


def test_cluster_detection_is_measurement_only():
    universe = GenesisUniverse(GenesisConfig(size=4))
    before = universe.phase.copy()
    LocalStructureObserver().detect(universe.phase)
    np.testing.assert_array_equal(before, universe.phase)


def test_boundary_contrast_is_zero_for_full_periodic_cluster():
    observer = LocalStructureObserver(threshold=0.99)
    cluster = observer.detect(np.zeros((4, 4)))[0]
    local = observer.local_coherence(np.zeros((4, 4)))
    assert observer.boundary_contrast(cluster, local) == pytest.approx(0.0)


def test_jaccard_identity_overlap():
    observer = LocalStructureObserver()
    tracker = RegionTracker(observer)
    phase = np.zeros((4, 4))
    a = observer.detect(phase)[0]
    b = observer.detect(phase)[0]
    assert tracker.jaccard(a, b) == pytest.approx(1.0)


def test_region_tracker_persists_identity_across_frames():
    observer = LocalStructureObserver(threshold=0.99)
    tracker = RegionTracker(observer)
    phase = np.zeros((4, 4))
    first = tracker.observe(phase)
    second = tracker.observe(phase)
    assert len(first) == len(second) == 1
    assert first[0].identity == second[0].identity
    assert first[0].lifetime == 1
    assert second[0].lifetime == 2
    assert second[0].persistence == 2
    assert second[0].overlap == pytest.approx(1.0)


def test_region_tracking_is_measurement_only():
    universe = GenesisUniverse(GenesisConfig(size=4))
    tracker = RegionTracker(LocalStructureObserver())
    before = universe.phase.copy()
    tracker.observe(universe.phase)
    np.testing.assert_array_equal(before, universe.phase)
