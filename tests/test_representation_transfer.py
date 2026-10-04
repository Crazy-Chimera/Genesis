from genesis.representation_transfer import RepresentationTransferPredictor


def test_transfer_rejects_invalid_configuration():
    import pytest
    with pytest.raises(ValueError):
        RepresentationTransferPredictor(components=0)
    with pytest.raises(ValueError):
        RepresentationTransferPredictor(history_length=1)
    with pytest.raises(ValueError):
        RepresentationTransferPredictor(ridge=-1)


def test_transfer_result_properties():
    from genesis.representation_transfer import RepresentationTransferResult
    result = RepresentationTransferResult(1, 2, 2, 2, 10, 1.0, 0.5, 0.8)
    assert result.improvement == 0.5
    assert result.beats_zero
    assert result.beats_shuffled
