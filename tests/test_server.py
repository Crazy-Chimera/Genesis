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


def test_dashboard_contains_genesis_pw001():
    html = render_dashboard({"tick": 0, "coherence": 0.5})
    assert "GENESIS-PW-001" in html
    assert "2.12" in html
    assert "State-difference trajectory · 2.13" in html
    assert "Nonlinear state trajectory · 2.14" in html
    assert "0/12 positive" in html
    assert "1/3 seeds positive" in html
    assert "negative; 7/54 zero-change wins" in html
    assert "0/6 beat zero-change" in html
    assert "0/18 positive" in html
    assert 'data-ui-version="2.25"' in html
    assert "state trajectory" in html.lower()
    assert "No self-model" in html
    assert "/step" in html


def test_dashboard_renders_live_state():
    html = render_dashboard({"tick": 123, "coherence": 0.123456789})
    assert "123" in html
    assert "0.123456789" in html
    assert "100,000" in html
