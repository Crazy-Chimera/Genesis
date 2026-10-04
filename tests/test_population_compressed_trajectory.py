from genesis.population_compressed_trajectory import PopulationCompressedTrajectoryPredictor


def test_population_compressed_invalid_config():
    for kwargs in (
        {"components": 0},
        {"history_length": 1},
        {"train_fraction": 0},
        {"train_fraction": 1},
        {"ridge": -1},
    ):
        try:
            PopulationCompressedTrajectoryPredictor(**kwargs)
        except ValueError:
            continue
        raise AssertionError(f"expected ValueError for {kwargs}")
