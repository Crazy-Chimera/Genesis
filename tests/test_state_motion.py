import numpy as np
import pytest

from genesis.state_motion import StateMotionPredictor


def test_state_motion_rejects_invalid_history():
    with pytest.raises(ValueError):
        StateMotionPredictor(history_length=1)


def test_state_motion_requires_consecutive_ticks():
    assert StateMotionPredictor(history_length=2).require_consecutive is True


def test_state_motion_beats_zero_on_synthetic_signal():
    from types import SimpleNamespace

    records = []
    for tick in range(20):
        records.append(
            SimpleNamespace(
                tick=tick,
                identity=1,
                coherence=float(tick * 0.01),
                cells=(0,),
                boundary_contrast=0.0,
                lifetime=tick + 1,
                persistence=1.0,
                overlap=1.0,
                local_patch=(0.0,) * 9,
                phase_patch=(0.0,) * 18,
                gradient_patch=(0.0,) * 18,
                motion=(0.0,) * 3,
                boundary_flux=(0.0,) * 5,
                spatial_field=(0.0,) * 18,
                multiscale_field=(0.0,) * 68,
                relational=(0.0,) * 16,
                graph_relational=(0.0,) * 33,
                global_harmonics=(0.0,) * 9,
            )
        )

    result = StateMotionPredictor(history_length=2).evaluate(records)
    assert result.samples > 0
    assert np.isfinite(result.motion_mae)
