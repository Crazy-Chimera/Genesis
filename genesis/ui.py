from __future__ import annotations

import html
import json
from typing import Mapping


def render_dashboard(state: Mapping[str, float | int]) -> str:
    """Render the current measurement-only GENESIS research dashboard."""
    tick = int(state.get("tick", 0))
    coherence = float(state.get("coherence", 0.0))
    progress = min(100.0, max(0.0, tick / 100_000 * 100))
    payload = json.dumps({"tick": tick, "coherence": coherence}, separators=(",", ":"))

    stages = [
        ("2.36", "Mechanistic one-step rule", "6/6 positive"),
        ("2.38", "Unseen-seed mechanistic validation", "12/12 positive"),
        ("2.39", "Coupling dose-response", "6/6 minimum at 0.01"),
        ("2.42", "Independent full-rule audit", "0 phase/coherence residual"),
        ("2.43", "Mechanistic horizon validation", "24/24 positive"),
        ("2.44", "Noise attribution", "validated"),
        ("2.45", "Numerical convergence", "6 seeds · 4 dt values"),
        ("2.46", "Mechanistic timestep refinement", "24/24 positive"),
        ("2.47", "Controlled coupling perturbation", "6/6 exact"),
        ("2.48", "Fine coupling resolution", "4/6 exact · 2/6 adjacent"),
        ("2.49–2.54", "Noise / fine-grid controls", "noise-dependent offsets"),
        ("2.55", "Grid-resolution scaling", "scaling control"),
        ("2.56", "Replicated grid-convergence control", "50 replicates · 4 steps"),
        ("2.57", "High-replication grid-scaling control", "200 replicates · 4 spacings"),
    ]

    stage_html = "".join(
        f'<div class="stage"><span class="dot"></span>'
        f'<span class="stage-id">{html.escape(version)}</span> '
        f'{html.escape(name)} · <span class="muted">{html.escape(result)}</span></div>'
        for version, name, result in stages
    )

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Agent Ω / GENESIS</title>
<style>
:root {{ color-scheme: dark; --bg:#071019; --panel:#0d1823; --line:#203244;
  --text:#e8f0f7; --muted:#8fa5b8; --accent:#73d2a4; --warn:#e2b96f; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--bg); color:var(--text);
  font:14px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace; }}
main {{ max-width:1180px; margin:0 auto; padding:24px; }}
header {{ display:flex; justify-content:space-between; gap:20px; align-items:flex-start;
  border-bottom:1px solid var(--line); padding-bottom:20px; }}
h1,h2,p {{ margin:0; }} h1 {{ font-size:22px; }} h2 {{ font-size:13px; color:var(--muted); margin-bottom:10px; }}
.grid {{ display:grid; grid-template-columns:repeat(12,1fr); gap:12px; margin-top:12px; }}
.card {{ background:var(--panel); border:1px solid var(--line); border-radius:10px; padding:16px; }}
.span-3 {{ grid-column:span 3; }} .span-4 {{ grid-column:span 4; }}
.span-6 {{ grid-column:span 6; }} .span-8 {{ grid-column:span 8; }} .span-12 {{ grid-column:span 12; }}
.metric {{ font-size:25px; font-weight:700; }} .muted {{ color:var(--muted); }}
.ok {{ color:var(--accent); }} .pending {{ color:var(--warn); }}
.row {{ display:flex; justify-content:space-between; gap:12px; margin:6px 0; }}
.badge {{ border:1px solid var(--line); border-radius:999px; padding:3px 8px; }}
button {{ background:var(--accent); color:#071019; border:0; border-radius:7px;
  padding:9px 13px; font:inherit; font-weight:700; cursor:pointer; }}
button:disabled {{ opacity:.5; cursor:wait; }}
.bar {{ height:8px; background:#182634; border-radius:99px; overflow:hidden; margin-top:10px; }}
.bar > i {{ display:block; height:100%; width:{progress:.4f}%; background:var(--accent); }}
.timeline {{ display:grid; gap:7px; }} .stage {{ display:flex; gap:8px; align-items:center; }}
.dot {{ width:8px; height:8px; border-radius:50%; background:var(--accent); flex:none; }}
.stage-id {{ min-width:72px; color:var(--accent); }}
pre {{ margin:0; white-space:pre-wrap; color:var(--muted); }}
@media(max-width:800px) {{ .span-3,.span-4,.span-6,.span-8 {{ grid-column:span 12; }} header {{ flex-direction:column; }} }}
</style>
</head>
<body>
<main data-ui-version="2.57-verified">
<header>
  <div>
    <div class="muted">AGENT Ω / GENESIS</div>
    <h1>PRIMORDIAL EMERGENCE LAB</h1>
    <p class="muted">GENESIS-PW-001 · measurement-only experimental substrate</p>
  </div>
  <button id="step">ADVANCE ONE TICK</button>
</header>

<section class="grid">
  <div class="card span-3"><h2>UNIVERSE</h2><div class="metric">PW-001</div><div class="muted">16×16 · 256 oscillators</div></div>
  <div class="card span-3"><h2>TICK</h2><div id="tick" class="metric">{tick:,}</div><div class="muted">target 100,000</div><div class="bar"><i id="progress"></i></div></div>
  <div class="card span-3"><h2>COHERENCE</h2><div id="coherence" class="metric">{coherence:.9f}</div><div class="muted">external observer measurement</div></div>
  <div class="card span-3"><h2>Ω STATUS</h2><div class="metric ok">OBSERVER</div><div class="muted">Agent Ω not activated</div></div>

  <div class="card span-4">
    <h2>OBSERVATION / VALIDATION STACK</h2>
    <div class="timeline">
      <div class="stage"><span class="dot"></span><span class="stage-id">1.0–2.35</span> Observer / transfer probes</div>
      <div class="stage"><span class="dot"></span><span class="stage-id">2.36–2.39</span> Mechanistic rule prediction</div>
      <div class="stage"><span class="dot"></span><span class="stage-id">2.42–2.46</span> Independent / numerical controls</div>
      <div class="stage"><span class="dot"></span><span class="stage-id">2.47–2.54</span> Coupling identification controls</div>
      {stage_html}
    </div>
  </div>

  <div class="card span-8">
    <h2>CURRENT FRONTIER · GENESIS-2.57</h2>
    <p><b>Replicated grid-convergence control for coupling selection.</b></p>
    <p class="muted" style="margin-top:8px">
      Actual coupling = 0.01. Noise = 0.001 and 0.002. Four grid spacings:
      0.00025, 0.000125, 0.0000625, 0.00003125. Each condition uses 50 independent replicates.
    </p>
    <div class="grid">
      <div class="card span-6"><h2>OBSERVED</h2>
        <span class="ok">mean signed offsets remain small</span><br>
        <span class="muted">95% bootstrap intervals are compatible with zero in the reported conditions</span>
      </div>
      <div class="card span-6"><h2>INTERPRETATION</h2>
        <span class="pending">noise / residual floor</span><br>
        <span class="muted">absolute selection error does not shrink proportionally with grid spacing</span>
      </div>
    </div>
  </div>

  <div class="card span-6">
    <h2>MECHANISTIC EVIDENCE</h2>
    <div class="row"><span>2.36 one-step</span><span class="badge ok">6/6</span></div>
    <div class="row"><span>2.38 unseen seeds</span><span class="badge ok">12/12</span></div>
    <div class="row"><span>2.43 horizons</span><span class="badge ok">24/24</span></div>
    <div class="row"><span>2.46 timestep refinement</span><span class="badge ok">24/24</span></div>
    <div class="row"><span>2.47 coupling perturbation</span><span class="badge ok">6/6</span></div>
    <p class="muted">These are external predictions derived from the specified computational rule, not evidence of intelligence or agency.</p>
  </div>

  <div class="card span-6">
    <h2>COUPLING IDENTIFICATION</h2>
    <div class="row"><span>2.48 fine grid</span><span class="badge">4/6 exact · 2/6 adjacent</span></div>
    <div class="row"><span>2.54 fine-grid control</span><span class="badge">15/15 conditions</span></div>
    <div class="row"><span>2.56 replicated control</span><span class="badge ok">200 replicates / condition</span></div>
    <p class="muted">Current question: does the coupling-selection residual shrink with grid refinement beyond the stochastic residual floor?</p>
  </div>

  <div class="card span-12">
    <h2>INVARIANTS</h2>
    <div class="grid">
      <div class="card span-3"><span class="ok">✓</span> Universe rules unchanged</div>
      <div class="card span-3"><span class="ok">✓</span> Observer is external</div>
      <div class="card span-3"><span class="ok">✓</span> Prediction has no feedback</div>
      <div class="card span-3"><span class="ok">✓</span> No endogenous memory</div>
      <div class="card span-3"><span class="ok">✓</span> No goals / reward</div>
      <div class="card span-3"><span class="ok">✓</span> No agency</div>
      <div class="card span-3"><span class="ok">✓</span> No self-model</div>
      <div class="card span-3"><span class="ok">✓</span> No AGI claim</div>
    </div>
  </div>

  <div class="card span-12">
    <h2>LIVE STATE</h2>
    <pre id="state">{html.escape(payload)}</pre>
  </div>
</section>
</main>
<script>
const tickEl=document.getElementById("tick"), coherenceEl=document.getElementById("coherence");
const progressEl=document.getElementById("progress"), stateEl=document.getElementById("state");
const button=document.getElementById("step");
function render(s) {{
  tickEl.textContent=Number(s.tick).toLocaleString();
  coherenceEl.textContent=Number(s.coherence).toFixed(9);
  progressEl.style.width=Math.min(100, Number(s.tick)/100000*100)+"%";
  stateEl.textContent=JSON.stringify(s);
}}
button.addEventListener("click", async () => {{
  button.disabled=true;
  try {{
    const response=await fetch("/step", {{cache:"no-store"}});
    if (!response.ok) throw new Error("step failed");
    render(await response.json());
  }} finally {{ button.disabled=false; }}
}});
window.addEventListener("load", async () => {{
  const response=await fetch("/state", {{cache:"no-store"}});
  if (response.ok) render(await response.json());
}});
</script>
</body>
</html>"""
