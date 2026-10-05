from genesis.core import GenesisConfig, GenesisUniverse
from genesis.memory import TemporalMemory
from genesis.observer import LocalStructureObserver, RegionTracker
from genesis.state_change import StateChangePredictor, state_change


def collect(ticks: int = 4):
    universe = GenesisUniverse(GenesisConfig(ticks=ticks))
    tracker = RegionTracker(LocalStructureObserver())
    memory = TemporalMemory()
    observations, events = tracker.observe_events(universe.phase)
    memory.record(universe.tick, observations, events)
    for _ in range(ticks):
        universe.step()
        observations, events = tracker.observe_events(universe.phase)
        memory.record(universe.tick, observations, events)
    return memory.all()


def test_state_change_has_compact_group_statistics():
    records = collect()
    same = next(r for r in records if r.tick == 0)
    later = next(r for r in records if r.tick == 1 and r.identity == same.identity)
    values = state_change(same, later)
    assert len(values) == 44
    assert all(value == value for value in values)


def test_state_change_predictor_validates_history():
    try:
        StateChangePredictor(history_length=1)
    except ValueError:
        pass
    else:
        raise AssertionError("history_length=1 must fail")


def test_state_change_predictor_handles_records():
    result = StateChangePredictor(history_length=2).evaluate(collect(8))
    assert result.samples >= 0
    assert result.zero_mae >= 0.0
    assert result.change_mae >= 0.0
