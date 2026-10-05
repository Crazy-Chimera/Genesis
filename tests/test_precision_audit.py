from genesis.core import GenesisConfig, GenesisUniverse
from genesis.precision_audit import evaluate_precision_audit


def test_precision_audit_rejects_invalid_horizon():
    try:
        evaluate_precision_audit(GenesisUniverse(GenesisConfig(ticks=1)), 0)
        assert False
    except ValueError:
        pass


def test_precision_audit_is_deterministic_and_bounded():
    result = evaluate_precision_audit(
        GenesisUniverse(GenesisConfig(ticks=3)),
        1,
    )
    assert result.samples == 3
    assert result.mean_coherence_gap >= 0.0
    assert result.max_coherence_gap >= result.mean_coherence_gap
    assert result.mean_phase_gap >= 0.0
    assert result.max_phase_gap >= result.mean_phase_gap
