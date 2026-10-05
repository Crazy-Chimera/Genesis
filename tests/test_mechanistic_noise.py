from genesis.core import GenesisConfig, GenesisUniverse
from genesis.mechanistic_noise import evaluate_noise_audit


def test_noise_audit_is_exact_for_deterministic_path():
    result = evaluate_noise_audit(
        GenesisUniverse(GenesisConfig(seed=390001, ticks=5)), 2
    )
    assert result.samples == 5
    assert result.deterministic_mae == 0.0


def test_noise_audit_rejects_invalid_horizon():
    universe = GenesisUniverse(GenesisConfig(ticks=1))
    try:
        evaluate_noise_audit(universe, 0)
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError")
