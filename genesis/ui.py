from __future__ import annotations

import html
import json
from typing import Mapping


def render_dashboard(state: Mapping[str, float | int]) -> str:
    """Render the measurement-only GENESIS chat dashboard."""
    tick = int(state.get("tick", 0))
    coherence = float(state.get("coherence", 0.0))
    progress = min(100.0, max(0.0, tick / 100_000 * 100))

    payload = json.dumps(
        {"tick": tick, "coherence": coherence},
        separators=(",", ":"),
    )

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Agent Ω / GENESIS</title>
<style>
:root {{
  color-scheme: dark;
  --bg:#071019; --panel:#0d1823; --panel2:#101e2b; --line:#203244;
  --text:#e8f0f7; --muted:#8fa5b8; --accent:#73d2a4; --warn:#e2b96f;
}}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--bg); color:var(--text);
  font:14px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace; }}
main {{ max-width:1180px; margin:0 auto; padding:24px; }}
header {{ display:flex; justify-content:space-between; gap:20px; align-items:flex-start;
  border-bottom:1px solid var(--line); padding-bottom:20px; }}
h1,h2,h3,p {{ margin:0; }}
h1 {{ font-size:22px; letter-spacing:.04em; }}
h2 {{ font-size:13px; color:var(--muted); margin-bottom:10px; }}
.grid {{ display:grid; grid-template-columns:repeat(12,1fr); gap:12px; margin-top:12px; }}
.card {{ background:var(--panel); border:1px solid var(--line); border-radius:10px; padding:16px; }}
.span-3 {{ grid-column:span 3; }} .span-4 {{ grid-column:span 4; }}
.span-6 {{ grid-column:span 6; }} .span-8 {{ grid-column:span 8; }}
.span-12 {{ grid-column:span 12; }}
.metric {{ font-size:25px; font-weight:700; }}
.muted {{ color:var(--muted); }}
.ok {{ color:var(--accent); }} .pending {{ color:var(--warn); }}
.row {{ display:flex; justify-content:space-between; gap:12px; margin:6px 0; }}
.badge {{ border:1px solid var(--line); border-radius:999px; padding:3px 8px; }}
button {{ background:var(--accent); color:#071019; border:0; border-radius:7px;
  padding:9px 13px; font:inherit; font-weight:700; cursor:pointer; }}
button:disabled {{ opacity:.5; cursor:wait; }}
.bar {{ height:8px; background:#182634; border-radius:99px; overflow:hidden; margin-top:10px; }}
.bar > i {{ display:block; height:100%; width:{progress:.4f}%; background:var(--accent); }}
.timeline {{ display:grid; gap:7px; }}
.stage {{ display:flex; gap:10px; align-items:center; }}
.dot {{ width:9px; height:9px; border-radius:50%; background:var(--accent); flex:none; }}
.dot.pending {{ background:var(--warn); }}
pre {{ margin:0; white-space:pre-wrap; color:var(--muted); }}
@media(max-width:800px) {{
  .span-3,.span-4,.span-6,.span-8 {{ grid-column:span 12; }}
  header {{ flex-direction:column; }}
}}
</style>
</head>
<body>
<main data-ui-version="2.17">
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
    <h2>OBSERVATION STACK</h2>
    <div class="timeline">
      <div class="stage"><span class="dot"></span>1. Coherence · 1.0</div>
      <div class="stage"><span class="dot"></span>2. Local structures · 1.1</div>
      <div class="stage"><span class="dot"></span>3. Persistence / identity · 1.2</div>
      <div class="stage"><span class="dot"></span>4. Lifecycle events · 1.3</div>
      <div class="stage"><span class="dot"></span>5. Temporal memory · 1.4</div>
      <div class="stage"><span class="dot"></span>6. Prediction · 1.5–1.6b</div>
      <div class="stage"><span class="dot"></span>7. Structural probes · 1.7–2.8</div>
      <div class="stage"><span class="dot"></span>8. Innovation · 2.9</div>
      <div class="stage"><span class="dot"></span>9. State reconstruction · 2.10–2.11</div>
      <div class="stage"><span class="dot"></span>10. State trajectory · 2.12 · <span class="muted">negative vs zero baseline</span></div>
      <div class="stage"><span class="dot"></span>11. State-difference trajectory · 2.13 · <span class="muted">12/12 below zero baseline</span></div>
      <div class="stage"><span class="dot"></span>12. Nonlinear state trajectory · 2.14 · <span class="muted">12/12 below zero baseline</span></div>
      <div class="stage"><span class="dot"></span>13. Representation bottleneck · 2.15 · <span class="muted">screening positive, not robust</span></div>
      <div class="stage"><span class="dot pending"></span>14. Full-length dim-2 validation · 2.16 · <span class="muted">not robust across seeds</span></div>
    </div>
  </div>

  <div class="card span-8">
    <h2>RESULT · GENESIS-2.16</h2>
    <p><b>Full-length validation of the isolated GENESIS-2.15 dim-2 positive case is running.</b></p>
    <div class="grid">
      <div class="card span-6"><h2>INPUT</h2><span class="ok">state(t-k) … state(t)</span><br><span class="muted">PCA-compressed 193D observer state · 2 components</span></div>
      <div class="card span-6"><h2>RESULT</h2><span class="pending">not robust</span><br><span class="muted">only seed 390003 beat zero-change</span></div>
      <div class="card span-6"><h2>TARGET</h2><span>ΔC(t+1) = C(t+1) − C(t)</span></div>
      <div class="card span-6"><h2>CONTROLS</h2><span>zero-change · shuffled trajectory</span></div>
    </div>
  </div>

  <div class="card span-6">
    <h2>EVIDENCE · 2.9</h2>
    <div class="row"><span>innovation predictor</span><span class="badge ok">12/12 positive</span></div>
    <div class="row"><span>seeds</span><span>390001 · 390002 · 390003</span></div>
    <div class="row"><span>history lengths</span><span>2 · 3 · 5 · 10</span></div>
    <p class="muted">Recent coherence changes predict the next change better than the zero-change baseline under the tested protocol.</p>
  </div>

  <div class="card span-6">
    <h2>EVIDENCE · 2.10–2.15</h2>
    <div class="row"><span>single state · 2.10</span><span class="badge pending">not robust</span></div>
    <div class="row"><span>combined 193D state · 2.11</span><span class="badge pending">not reconstructed</span></div>
    <div class="row"><span>state trajectory · 2.12</span><span class="badge pending">12/12 below zero baseline</span></div>
    <div class="row"><span>nonlinear trajectory · 2.14</span><span class="badge pending">12/12 below zero baseline</span></div>
    <div class="row"><span>representation bottleneck · 2.15</span><span class="badge pending">screening only</span></div>\n    <div class="row"><span>dim-2 full validation · 2.16</span><span class="badge pending">1/3 seeds positive</span></div>
    <p class="muted">Neither a single state, combined 193D state, short state trajectory, nor nonlinear trajectory reconstructs the 2.9 innovation signal robustly. 2.15 produced one screening-positive dim-2 case (seed 390001). 2.16 full-length validation found a positive result only for seed 390003; seeds 390001 and 390002 remained below the zero-change baseline.</p>
  </div>

  <div class="card span-12">
    <h2>NEXT · GENESIS-2.16</h2>
    <p><b>Full-length validation of the dim-2 representation.</b></p>
    <p class="muted">2.15 found an isolated positive result at two PCA components for seed 390001. 2.16 tests that exact representation over 10,000 ticks and all three seeds before any claim of robust predictive structure is allowed.</p>
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
const tickEl=document.getElementById("tick");
const coherenceEl=document.getElementById("coherence");
const progressEl=document.getElementById("progress");
const stateEl=document.getElementById("state");
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
  }} finally {{
    button.disabled=false;
  }}
}});

window.addEventListener("load", async () => {{
  const response=await fetch("/state", {{cache:"no-store"}});
  if (response.ok) render(await response.json());
}});
</script>
</body>
</html>"""
