from genesis.server import GenesisServer
from genesis.ui import render_dashboard


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


def test_dashboard_contains_current_genesis_frontier():
    html = render_dashboard({"tick": 0, "coherence": 0.5})
    assert "GENESIS-PW-001" in html
    assert 'data-ui-version="2.57-verified"' in html
    assert "GENESIS-2.57" in html
    assert "2.56" in html
    assert "High-replication grid-scaling control" in html
    assert "200 replicates / condition" in html
    assert "2.48 fine grid" in html
    assert "6/6 minimum at 0.01" in html
    assert "24/24 positive" in html
    assert "No self-model" in html
    assert "No AGI claim" in html
    assert "/step" in html


def test_dashboard_renders_live_state():
    html = render_dashboard({"tick": 123, "coherence": 0.123456789})
    assert "123" in html
    assert "0.123456789" in html
    assert "100,000" in html
