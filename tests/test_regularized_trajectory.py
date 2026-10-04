from genesis.regularized_trajectory import evaluate_ridge_sweep


def test_ridge_sweep_returns_requested_grid():
    assert [r.ridge for r in evaluate_ridge_sweep([], ridge_grid=(0.0, 1.0))] == [0.0, 1.0]


def test_ridge_sweep_validates_grid():
    try:
        evaluate_ridge_sweep([], ridge_grid=())
    except ValueError:
        pass
    else:
        raise AssertionError("empty ridge grid must fail")
