import numpy as np

from genesis.memory import MemoryRecord
from genesis.state_difference import StateDifferencePredictor
from genesis.state_innovation import StateFeatureSpec


def test_state_difference_rejects_invalid_history():
    try:
        StateDifferencePredictor(history_length=1)
    except ValueError:
        return
    raise AssertionError("history_length=1 must fail")


def test_state_difference_rejects_unknown_feature():
    try:
        StateDifferencePredictor(feature_name="missing")
    except ValueError:
        return
    raise AssertionError("unknown feature must fail")


def test_state_difference_skips_invalid_feature_widths():
    records = [
        MemoryRecord(
            tick=t,
            identity=1,
            cells=((0, 0),),
            coherence=0.1 + 0.001 * t,
            boundary_contrast=0.0,
            lifetime=t + 1,
            persistence=t + 1,
            overlap=1.0,
            spatial_field=(float(t),) + (0.0,) * 17,
        )
        for t in range(8)
    ]
    predictor = StateDifferencePredictor(
        feature_name="spatial_field",
        history_length=2,
    )
    predictor.spec = StateFeatureSpec(
        "synthetic",
        lambda record: (
            (float(record.tick),)
            if record.tick % 2 == 0
            else (float(record.tick), 0.0)
        ),
        1,
    )
    result = predictor.evaluate(records)
    assert result.samples == 0
