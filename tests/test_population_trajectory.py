import pytest
from genesis.population_trajectory import PopulationTrajectoryPredictor


def test_population_trajectory_validates_history():
    with pytest.raises(ValueError):
        PopulationTrajectoryPredictor(history_length=1)


def test_population_trajectory_validates_ridge():
    with pytest.raises(ValueError):
        PopulationTrajectoryPredictor(ridge=-1)
