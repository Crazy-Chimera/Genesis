from genesis.state_trajectory_compressed import CompressedStateTrajectoryPredictor


def test_invalid_components():
    try:
        CompressedStateTrajectoryPredictor(components=0)
    except ValueError:
        pass
    else:
        raise AssertionError("components=0 must fail")


def test_invalid_component_width():
    try:
        CompressedStateTrajectoryPredictor(feature_name="motion", components=4)
    except ValueError:
        pass
    else:
        raise AssertionError("components wider than feature must fail")
