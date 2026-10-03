from genesis import Cluster, LocalStructureObserver, RegionTracker
from genesis.memory import TemporalMemory


def test_temporal_memory_records_observation_and_event():
    tracker = RegionTracker(LocalStructureObserver(threshold=0.99))
    memory = TemporalMemory()

    phase = __import__("numpy").zeros((4, 4))
    observations, events = tracker.observe_events(phase)
    records = memory.record(0, observations, events)

    assert len(records) == 1
    assert records[0].tick == 0
    assert records[0].identity == 1
    assert records[0].events == ("birth",)


def test_temporal_memory_preserves_history_without_mutating_observation():
    tracker = RegionTracker(LocalStructureObserver(threshold=0.99))
    memory = TemporalMemory()
    phase = __import__("numpy").zeros((4, 4))

    observations, events = tracker.observe_events(phase)
    memory.record(0, observations, events)
    observations, events = tracker.observe_events(phase)
    memory.record(1, observations, events)

    history = memory.for_identity(1)
    assert len(history) == 2
    assert history[0].tick == 0
    assert history[1].tick == 1
    assert history[1].persistence == 2
    assert memory.at_tick(0) == (history[0],)
