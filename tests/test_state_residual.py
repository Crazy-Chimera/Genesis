from __future__ import annotations

import pytest

from genesis.state_residual import StateResidualTrajectoryPredictor


def test_invalid_history():
    with pytest.raises(ValueError):
        StateResidualTrajectoryPredictor(history_length=1)


def test_invalid_fraction():
    with pytest.raises(ValueError):
        StateResidualTrajectoryPredictor(train_fraction=1.0)


def test_invalid_feature():
    with pytest.raises(ValueError):
        StateResidualTrajectoryPredictor(feature_name="missing")


def test_invalid_ridge():
    with pytest.raises(ValueError):
        StateResidualTrajectoryPredictor(ridge=-1.0)
