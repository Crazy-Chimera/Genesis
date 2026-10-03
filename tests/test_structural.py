import pytest

from genesis.memory import MemoryRecord
from genesis.structural import StructuralPredictor, structural_features


def record(
    tick: int,
    coherence: float,
    *,
    size: int = 1,
    boundary: float = 0.1,
    lifetime: int = 1,
    persistence: int = 1,
    overlap: float = 1.0,
) -> MemoryRecord:
    cells = tuple((0, i) for i in range(size))
    return MemoryRecord(
        tick=tick,
        identity=1,
        cells=cells,
        coherence=coherence,
        boundary_contrast=boundary,
        lifetime=lifetime,
        persistence=persistence,
        overlap=overlap,
    )


def test_structural_features_exclude_coherence():
    item = record(0, coherence=0.99, size=3, boundary=0.2)
    assert structural_features(item) == (3.0, 0.2, 1.0, 1.0, 1.0)


def test_structure_only_predictor_beats_persistence_on_synthetic_relation():
    records = [
        record(
            tick=t,
            coherence=0.2 + 0.01 * (t % 5),
            size=1 + (t % 4),
            boundary=0.05 * (t % 4),
            lifetime=1 + (t % 4),
            persistence=1 + (t % 4),
            overlap=0.2 * (t % 4),
        )
        for t in range(40)
    ]
    # Make the target explicitly dependent on the previous structural size.
    records = [
        record(
            tick=item.tick,
            coherence=0.1 + 0.05 * len(
                records[item.tick - 1].cells
            ) if item.tick else item.coherence,
            size=len(item.cells),
            boundary=item.boundary_contrast,
            lifetime=item.lifetime,
            persistence=item.persistence,
            overlap=item.overlap,
        )
        for item in records
    ]

    result = StructuralPredictor(train_fraction=0.5).evaluate(records)
    assert result.samples > 0
    assert result.structural_mae < result.baseline_mae


def test_structure_only_predictor_rejects_invalid_configuration():
    with pytest.raises(ValueError):
        StructuralPredictor(train_fraction=0.0)
    with pytest.raises(ValueError):
        StructuralPredictor(train_fraction=1.0)
    with pytest.raises(ValueError):
        StructuralPredictor(ridge=-1.0)


def test_structure_only_predictor_requires_consecutive_records():
    records = [
        record(0, 0.1),
        record(1, 0.2),
        record(3, 0.4),
        record(5, 0.5),
        record(7, 0.7),
    ]
    result = StructuralPredictor(require_consecutive=True).evaluate(records)
    assert result.samples == 0


def test_structure_only_predictor_accepts_single_feature():
    records = [
        record(
            tick=t,
            coherence=0.1 + 0.02 * (t % 4),
            size=1 + (t % 4),
            boundary=0.1,
            lifetime=1,
            persistence=1,
            overlap=1.0,
        )
        for t in range(40)
    ]
    result = StructuralPredictor(train_fraction=0.5).evaluate(records, ("size",))
    assert result.samples > 0
    assert result.feature_names == ("size",)


def test_structure_only_predictor_rejects_unknown_feature():
    with pytest.raises(ValueError):
        StructuralPredictor().evaluate([record(0, 0.1)], ("unknown",))
