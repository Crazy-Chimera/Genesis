from genesis.state_trajectory_regularized import RegularizedStateTrajectoryPredictor


def test_regularized_predictor_rejects_invalid_config():
    for kwargs in (
        {"history_length": 1},
        {"train_fraction": 0},
        {"validation_fraction": 1},
        {"ridges": ()},
        {"ridges": (-1.0,)},
    ):
        try:
            RegularizedStateTrajectoryPredictor(**kwargs)
        except ValueError:
            continue
        raise AssertionError(f"accepted invalid config: {kwargs}")


def test_regularized_predictor_handles_empty_records():
    result = RegularizedStateTrajectoryPredictor().evaluate([])
    assert result.samples == 0
