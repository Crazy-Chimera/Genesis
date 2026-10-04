from genesis.state_difference_trajectory import StateDifferenceTrajectoryPredictor


def test_rejects_invalid_history_length():
    try:
        StateDifferenceTrajectoryPredictor(history_length=1)
    except ValueError:
        return
    raise AssertionError("expected ValueError")


def test_rejects_invalid_ridge():
    try:
        StateDifferenceTrajectoryPredictor(ridge=-1.0)
    except ValueError:
        return
    raise AssertionError("expected ValueError")


def test_empty_records_are_safe():
    result = StateDifferenceTrajectoryPredictor().evaluate([])
    assert result.samples == 0
    assert result.improvement == 0.0
