from genesis.state_difference import StateDifferencePredictor


def test_state_difference_predictor_validates_history():
    try:
        StateDifferencePredictor(history_length=1)
    except ValueError:
        return
    raise AssertionError("history_length=1 must be rejected")


def test_state_difference_predictor_rejects_unknown_feature():
    try:
        StateDifferencePredictor(feature_name="missing")
    except ValueError:
        return
    raise AssertionError("unknown feature must be rejected")
