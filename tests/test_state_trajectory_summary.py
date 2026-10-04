import numpy as np
import pytest

from genesis.state_trajectory_summary import (
    TrajectorySummaryPredictor,
    summarize_vectors,
)


def test_summary_has_expected_width():
    vectors = [tuple(float(i) for i in range(3)) for _ in range(4)]
    assert len(summarize_vectors(vectors)) == 5 * 4 + 4 * 3


def test_summary_rejects_short_trajectory():
    with pytest.raises(ValueError):
        summarize_vectors([(1.0, 2.0)])


def test_predictor_rejects_history_below_two():
    with pytest.raises(ValueError):
        TrajectorySummaryPredictor(history_length=1)


def test_summary_contains_finite_values():
    vectors = [
        (1.0, 2.0, 3.0),
        (1.5, 2.5, 3.5),
        (2.0, 3.0, 4.0),
    ]
    assert np.isfinite(summarize_vectors(vectors)).all()
