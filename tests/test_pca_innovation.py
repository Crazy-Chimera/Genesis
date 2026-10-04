import pytest

from genesis.memory import MemoryRecord
from genesis.pca_innovation import PCAStateInnovationPredictor


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
        local_patch=(x,) + (0.0,) * 8,
        gradient_patch=(x,) + (0.0,) * 17,
        motion=(x, 0.0, 0.0),
        boundary_flux=(x,) + (0.0,) * 4,
        spatial_field=(x,) + (0.0,) * 17,
        multiscale_field=(x,) + (0.0,) * 67,
        relational=(x,) + (0.0,) * 15,
        graph_relational=(x,) + (0.0,) * 32,
    )


def test_pca_innovation_can_recover_synthetic_relation() -> None:
    records = []
    coherence = 0.2
    for tick in range(40):
        if tick:
            coherence += 0.001 * (tick - 1)
        records.append(make_record(tick, float(tick), coherence))

    result = PCAStateInnovationPredictor(
        components=2, train_fraction=0.5, require_consecutive=True
    ).evaluate(records)

    assert result.samples > 0
    assert result.beats_zero
    assert result.beats_shuffled


def test_pca_innovation_rejects_invalid_components() -> None:
    with pytest.raises(ValueError):
        PCAStateInnovationPredictor(components=0)
    with pytest.raises(ValueError):
        PCAStateInnovationPredictor(components=194)


def test_pca_innovation_rejects_non_consecutive_pairs() -> None:
    records = [make_record(tick, float(tick), 0.2 + 0.001 * tick)
               for tick in range(0, 20, 2)]
    result = PCAStateInnovationPredictor(components=2).evaluate(records)
    assert result.samples == 0
