import pytest

from genesis.memory import MemoryRecord
from genesis.state_innovation import StateInnovationPredictor


def make_record(tick: int, x: float, coherence: float) -> MemoryRecord:
    return MemoryRecord(
        tick=tick,
        identity=1,
        cells=((0, 0),),
        coherence=coherence,
        boundary_contrast=0.0,
        lifetime=tick + 1,
        persistence=tick + 1,
        overlap=1.0,
        phase_patch=(x,) + (0.0,) * 17,
    )


def test_state_innovation_can_recover_synthetic_relation() -> None:
    records = []
    coherence = 0.2
    for tick in range(20):
        if tick:
            coherence += 0.001 * (tick - 1)
        records.append(make_record(tick, float(tick), coherence))

    result = StateInnovationPredictor(
        "phase_patch", train_fraction=0.5, require_consecutive=True
    ).evaluate(records)

    assert result.samples > 0
    assert result.beats_zero
    assert result.beats_shuffled


def test_state_innovation_rejects_unknown_feature() -> None:
    with pytest.raises(ValueError):
        StateInnovationPredictor("coherence")


def test_state_innovation_rejects_non_consecutive_pairs() -> None:
    records = [
        make_record(tick, float(tick), 0.2 + 0.001 * tick)
        for tick in range(0, 20, 2)
    ]
    result = StateInnovationPredictor("phase_patch").evaluate(records)
    assert result.samples == 0
