from genesis.seed_invariant import SeedInvariantPredictor


def test_rejects_invalid_history():
    try:
        SeedInvariantPredictor(history_length=1)
    except ValueError:
        return
    raise AssertionError("history_length=1 must fail")


def test_rejects_negative_ridge():
    try:
        SeedInvariantPredictor(ridge=-1)
    except ValueError:
        return
    raise AssertionError("negative ridge must fail")
