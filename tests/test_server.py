from genesis.server import GenesisServer


def test_server_state_starts_at_zero():
    app = GenesisServer()
    state = app.state()
    assert state["tick"] == 0
    assert 0.0 <= state["coherence"] <= 1.0


def test_server_step_advances_universe():
    app = GenesisServer()
    state = app.step()
    assert state["tick"] == 1
    assert 0.0 <= state["coherence"] <= 1.0
