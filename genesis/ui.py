from __future__ import annotations

import html
import json
from typing import Mapping


def render_dashboard(state: Mapping[str, float | int]) -> str:
    """Render the measurement-only GENESIS research dashboard."""
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
<main data-ui-version="2.44-verified">
<header>
  <div>
    <div class="muted">AGENT Ω / GENESIS</div>
    <h1>PRIMORDIAL EMERGENCE LAB</h1>
    <p class="muted">GENESIS-PW-001 · measurement-only experimental substrate</p>
  </div>
  <button id="step">ADVANCE ONE TICK</button>
</header>

<section class="grid">
  <div class="card span-3"><h2>UNIVERSE</h2><div class="metric">PW-001</div><div class="muted">16×16 · 256 oscillators<div class="stage"><span class="dot pending"></span>32. Independent unseen-seed rule-transition replication · 2.32 · <span class="muted">4/12 baseline; negative mean</span></div><div class="stage"><span class="dot pending"></span>33. Rule-transition permutation audit · 2.33 · <span class="muted">3/12 p&lt;0.05; insufficient</span></div></div>
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
      <div class="stage"><span class="dot"></span>8. Innovation · 2.9 · <span class="muted">12/12 positive</span></div>
      <div class="stage"><span class="dot"></span>9. State reconstruction · 2.10–2.11 · <span class="muted">not robust</span></div>
      <div class="stage"><span class="dot"></span>10. State trajectory · 2.12 · <span class="muted">0/12 positive</span></div>
      <div class="stage"><span class="dot"></span>11. State-difference / harmonic-state probes · 2.13 · <span class="muted">validation in progress</span></div>
      <div class="stage"><span class="dot"></span>12. Nonlinear state trajectory · 2.14 · <span class="muted">0/12 positive</span></div>
      <div class="stage"><span class="dot"></span>13. Representation bottleneck · 2.15 · <span class="muted">screening only</span></div>
      <div class="stage"><span class="dot"></span>14. Full-length dim-2 validation · 2.16 · <span class="muted">1/3 seeds positive</span></div>
      <div class="stage"><span class="dot"></span>15. Population-state innovation · 2.17 · <span class="muted">1/3 positive; no shuffled win</span></div>
      <div class="stage"><span class="dot"></span>16. Population-state trajectory · 2.18 · <span class="muted">0/12 positive</span></div>
      <div class="stage"><span class="dot"></span>17. Population representation bottleneck · 2.19 · <span class="muted">0/24 positive</span></div>
      <div class="stage"><span class="dot pending"></span>18. Cross-seed representation transfer · 2.20 · <span class="muted">negative; 7/54 zero-change wins</span></div>\n      <div class="stage"><span class="dot"></span>19. Leave-one-seed-out generalization · 2.21 · <span class="muted">0/9 positive</span></div>\n      <div class="stage"><span class="dot"></span>20. Seed-invariant generalization · 2.22 · <span class="muted">0/9 positive</span></div>\n      <div class="stage"><span class="dot"></span>21. Expanded cross-seed generalization · 2.23 · <span class="muted">0/18 positive</span></div>\n      <div class="stage"><span class="dot"></span>22. Rule-native cross-seed screening · 2.24 · <span class="muted">0/6 positive</span></div>\n      <div class="stage"><span class="dot pending"></span>23. Rule-update cross-seed screening · 2.25 · <span class="muted">0/6 positive</span>\n      <div class="stage"><span class="dot"></span>24. Rule-invariant validation · 2.26 · <span class="muted">CI green</span></div>\n      <div class="stage"><span class="dot pending"></span>25. Rule-distribution cross-seed screening · 2.27 · <span class="muted">0/6 positive</span></div>
      <div class="stage"><span class="dot"></span>26. Rule-invariant validation · 2.26 · <span class="muted">CI green</span></div>
      <div class="stage"><span class="dot"></span>27. Rule-distribution screening · 2.27 · <span class="muted">0/6 positive</span></div>
      <div class="stage"><span class="dot"></span>28. Rule-transition cross-seed · 2.28 · <span class="muted">4/6 baseline wins</span></div>
      <div class="stage"><span class="dot pending"></span>29. Blocked-time rule-transition · 2.29 · <span class="muted">4/6 baseline; 1/6 shuffled</span></div>
      <div class="stage"><span class="dot pending"></span>30. Unseen-seed replication · 2.30 · <span class="muted">2/6 baseline; 3/6 shuffled</span></div>
      <div class="stage"><span class="dot pending"></span>31. Extended unseen-seed replication · 2.31 · <span class="muted">4/12 baseline; 5/12 shuffled</span></div><div class="stage"><span class="dot"></span>32. Mechanistic one-step rule · 2.36 · <span class="muted">6/6 positive</span></div><div class="stage"><span class="dot"></span>33. Coupling decomposition · 2.37 · <span class="muted">6/6 full-rule wins</span></div><div class="stage"><span class="dot"></span>34. Coupling dose-response · 2.39 · <span class="muted">6/6 best at 0.01</span></div><div class="stage"><span class="dot"></span>35. Independent full-rule audit · 2.42 · <span class="muted">0 residual error across 6 seeds</span></div><div class="stage"><span class="dot"></span>36. Mechanistic horizon validation · 2.43 · <span class="muted">24/24 positive</span></div><div class="stage"><span class="dot"></span>37. Mechanistic noise attribution · 2.44 · <span class="muted">noise effect measured; attribution audit</span></div></div>
    </div>
  </div>

  <div class="card span-8">
    <h2>RESULT · GENESIS-2.43 VERIFIED</h2>
    <p><b>The mechanistic PW-001 predictor remains substantially better than zero-change through horizon 10 on all six unseen seeds tested in 2.43.</b></p>
    <div class="grid">
      <div class="card span-6"><h2>INPUT</h2><span class="ok">explicit PW-001 rule</span><br><span class="muted">6 unseen seeds · horizons 1, 2, 5, 10</span></div>
      <div class="card span-6"><h2>RESULT</h2><span class="ok">2.43 positive · 24/24 seed×horizon cases</span><br><span class="muted">deterministic rule prediction vs zero-change; no feedback into the universe</span></div>
      <div class="card span-6"><h2>TARGET</h2><span>next coherence innovation ΔC</span></div>
      <div class="card span-6"><h2>CONTROLS</h2><span>zero-change · shuffled representation</span></div>
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
    <h2>EVIDENCE · 2.10–2.37</h2>
    <div class="row"><span>single state · 2.10</span><span class="badge pending">not robust</span></div>
    <div class="row"><span>combined 193D state · 2.11</span><span class="badge pending">not reconstructed</span></div>
    <div class="row"><span>state trajectory · 2.12</span><span class="badge pending">0/12 positive</span></div>
    <div class="row"><span>2.13 state-change / harmonic probes</span><span class="badge pending">validation in progress</span></div>
    <div class="row"><span>nonlinear trajectory · 2.14</span><span class="badge pending">0/12 positive</span></div>
    <div class="row"><span>representation bottleneck · 2.15</span><span class="badge pending">screening only</span></div>
    <div class="row"><span>dim-2 full validation · 2.16</span><span class="badge pending">1/3 seeds positive</span></div>
    <div class="row"><span>population-state innovation · 2.17</span><span class="badge pending">1/3 positive; no shuffled win</span></div>
    <div class="row"><span>population trajectory · 2.18</span><span class="badge pending">0/12 positive</span></div>
    <div class="row"><span>population PCA bottleneck · 2.19</span><span class="badge pending">0/24 positive</span></div>
    <div class="row"><span>cross-seed transfer · 2.20</span><span class="badge pending">7/54 positive</span></div>\n    <div class="row"><span>leave-one-seed-out · 2.21</span><span class="badge pending">0/9 positive</span></div>\n    <div class="row"><span>seed-invariant · 2.22</span><span class="badge pending">0/9 positive</span></div>
    <div class="row"><span>expanded cross-seed · 2.23</span><span class="badge pending">0/18 positive</span></div>\n    <div class="row"><span>rule-native · 2.24</span><span class="badge pending">0/6 positive</span></div>\n    <div class="row"><span>rule-update · 2.25</span><span class="badge pending">0/6 positive</span></div>\n    <div class="row"><span>rule-invariant validation · 2.26</span><span class="badge ok">CI green</span></div>\n    <div class="row"><span>rule-distribution · 2.27</span><span class="badge pending">0/6 positive</span></div><div class="row"><span>unseen-seed replication · 2.32</span><span class="badge pending">4/12; negative mean</span></div><div class="row"><span>permutation audit · 2.33</span><span class="badge pending">3/12 p&lt;0.05</span></div><div class="row"><span>global-phase transfer · 2.35</span><span class="badge pending">0/3 positive</span></div><div class="row"><span>mechanistic one-step rule · 2.36</span><span class="badge ok">6/6 positive</span></div><div class="row"><span>coupling dose-response · 2.39</span><span class="badge ok">6/6 minimum at 0.01</span></div>
    <p class="muted">The tested observer-state families and rule-derived representations do not establish robust cross-seed predictive generalization. The primary criterion remains held-out improvement over zero-change; shuffled superiority alone is insufficient.</p>
  </div>

  <div class="card span-12">
    <h2>RESULT · GENESIS-2.36</h2>
    <p><b>Mechanistic one-step rule benchmark is positive across six independent seeds.</b></p>
    <p class="muted">2.32–2.35 remained negative. 2.36 applies the explicit PW-001 update equation without the stochastic noise term and predicts the next coherence innovation one step ahead. Across seeds 390001–390006, it beats zero-change in 6/6 cases, with mechanistic MAE ≈3.49–3.55×10⁻⁷ versus zero-change MAE ≈3.63×10⁻⁶–1.68×10⁻⁵.</p>
  </div>

<div class="card s8"><h2>RESULT · GENESIS-2.38</h2>
<p><b>Local coupling contributes predictive information beyond intrinsic frequency alone.</b></p>
<div class="grid">
<div class="card s6"><h2>BASE</h2><span class="muted">frequency-only update</span><br>
<span class="ok">intrinsic frequency + no coupling</span></div>
<div class="card s6"><h2>FULL RULE</h2><span class="muted">PW-001 deterministic update</span><br>
<span class="ok">frequency + local four-neighbour coupling</span></div>
<div class="card s6"><h2>RESULT</h2><span class="pending">12/12 unseen seeds</span><br>
<span class="muted">current CI benchmark · 390001–390006</span></div>
<div class="card s6"><h2>INTERPRETATION</h2><span class="muted">unseen-seed mechanistic validation; verified</span><br>
<span>prediction remains external and no-feedback</span></div>
</div></div>


  <div class="card span-12">
    <h2>RESULT · GENESIS-2.39</h2>
    <p><b>The coupling dose-response is centered on the actual PW-001 coupling value 0.01 across six unseen seeds.</b></p>
    <p class="muted">The tested values 0, 0.0025, 0.005, 0.0075, 0.01, 0.0125, 0.015 and 0.02 produce a unique minimum at 0.01 for every seed 390037–390042. This supports a mechanistic parameter-identification interpretation, while remaining external and no-feedback.</p>
  </div>

  <div class="card span-12">
    <h2>RESULT · GENESIS-2.42</h2>
    <p><b>Independent full-rule implementation reproduces the production PW-001 update exactly.</b></p>
    <p class="muted">Six seeds (390049–390054), 2,000 ticks each: maximum circular phase error = 0 and maximum coherence error = 0. The independent implementation includes the deterministic noise term and the same local coupling rule. This is an implementation-consistency result, not evidence of a new physical mechanism.</p>
  </div>

  <div class="card span-12">
    <h2>RESULT · GENESIS-2.44</h2>\n    <p><b>Independent noise-attribution audit isolates the stochastic contribution without changing the universe rule.</b></p>\n    <p class="muted">Six seeds × four horizons (1, 2, 5, 10): deterministic-reference MAE is 0 in the tested comparison, while the measured noise effect remains non-zero and grows with horizon. This is an attribution/validation result, not evidence of agency or a new physical mechanism.</p>\n  </div>\n\n  <div class="card span-12">\n    <h2>INVARIANTS</h2>
    <div class="grid">
      <div class="card span-3"><span class="ok">✓</span> Universe rules unchanged</div>
      <div class="card span-3"><span class="ok">✓</span> Observer is external</div>
      <div class="card span-3"><span class="ok">✓</span> Prediction has no feedback</div>
      <div class="card span-3"><span class="ok">✓</span> No endogenous memory</div>
      <div class="card span-3"><span class="ok">✓</span> No goals / reward</div>
      <div class="card span-3"><span class="ok">✓</span> No agency</div>
      <div class="card span-3"><span class="ok">✓</span> No self-model</div>
      <div class="card span-3"><span class="ok">✓</span> 2.10–2.42 results recorded</div>
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
