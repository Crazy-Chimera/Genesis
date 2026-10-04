from genesis.direct_state_transfer import DirectStateTransferPredictor, DirectTransferResult


def test_direct_transfer_rejects_invalid_configuration():
    import pytest
    with pytest.raises(ValueError):
        DirectStateTransferPredictor(history_length=1)
    with pytest.raises(ValueError):
        DirectStateTransferPredictor(ridge=-1)


def test_direct_transfer_result_properties():
    result = DirectTransferResult(1, 2, 2, 10, 1.0, 0.5, 0.8)
    assert result.improvement == 0.5
    assert result.beats_zero
    assert result.beats_shuffled
