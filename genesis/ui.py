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
button.secondary {{ background:transparent; color:var(--text); border:1px solid var(--line); }}
.controls {{ display:flex; gap:8px; flex-wrap:wrap; }}
#oscillators {{ display:block; width:100%; height:auto; aspect-ratio:1/1; background:#071019; border:1px solid var(--line); border-radius:8px; }}
.legend {{ display:flex; justify-content:space-between; gap:10px; margin-top:8px; color:var(--muted); font-size:12px; }}
.bar {{ height:8px; background:#182634; border-radius:99px; overflow:hidden; margin-top:10px; }}
.bar > i {{ display:block; height:100%; width:{progress:.4f}%; background:var(--accent); }}
.timeline {{ display:grid; gap:7px; }} .stage {{ display:flex; gap:8px; align-items:center; }}
.dot {{ width:8px; height:8px; border-radius:50%; background:var(--accent); flex:none; }}
.stage-id {{ min-width:72px; color:var(--accent); }}
pre {{ margin:0; white-space:pre-wrap; color:var(--muted); }}

/* ELS-0.1 is an external research layer; it does not alter universe state. */
.els-banner {{ margin:18px 0 8px; border:1px solid #41634f; background:linear-gradient(120deg,#10251f,#0d1823 70%); border-radius:10px; padding:18px; }}
.els-kicker {{ color:var(--accent); letter-spacing:.12em; font-size:11px; margin-bottom:6px; }}
.els-layout {{ display:grid; grid-template-columns: minmax(0,1fr) minmax(280px,.85fr); gap:12px; margin-top:12px; }}
.els-input {{ width:100%; background:#071019; color:var(--text); border:1px solid var(--line); border-radius:7px; padding:10px; font:inherit; margin:6px 0 10px; }}
.els-log {{ height:220px; overflow-y:auto; overscroll-behavior:contain; border:1px solid var(--line); border-radius:7px; padding:10px; background:#071019; }}
.els-entry {{ padding:8px 0; border-bottom:1px solid var(--line); overflow-wrap:anywhere; }}
.els-entry:last-child {{ border-bottom:0; }}
.els-entry time {{ color:var(--accent); font-size:11px; display:block; }}
.scroll-hint {{ color:var(--muted); font-size:11px; margin-top:6px; }}
@media(max-width:800px) { .els-layout { grid-template-columns:1fr; } }

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
  <div class="controls"><button id="step">ADVANCE ONE TICK</button><button id="live" class="secondary">START LIVE</button></div>
</header>


<section class="els-banner" aria-labelledby="els-title">
  <div class="els-kicker">EXTERNAL RESEARCH LAYER · ELS-0.1</div>
  <h1 id="els-title" style="font-size:19px">GENESIS: ELS-0.1</h1>
  <p style="margin-top:8px">Research notebook above GENESIS-PW-001. It records researcher hypotheses, annotations, and UI actions outside the simulated universe. Nothing entered here is fed back into the universe, observer, or predictor.</p>
  <div class="row" style="margin-top:12px"><span class="muted">Boundary</span><span class="badge ok">EXTERNAL · NO FEEDBACK</span></div>
  <div class="els-layout">
    <div class="card">
      <h2>RESEARCH ENTRY</h2>
      <label for="els-hypothesis">Hypothesis / question</label>
      <input class="els-input" id="els-hypothesis" maxlength="500" placeholder="What are we testing or trying to falsify?">
      <label for="els-note">Observation / interpretation</label>
      <textarea class="els-input" id="els-note" rows="4" maxlength="5000" placeholder="Record evidence, anomalies, caveats, or next steps…"></textarea>
      <div class="controls">
        <button id="els-record">RECORD NOTE</button>
        <button id="els-save" class="secondary">SAVE LOG (.JSON)</button>
        <button id="els-export-text" class="secondary">EXPORT TEXT (.TXT)</button>
      </div>
      <p class="scroll-hint">Entries auto-save in this browser. Use Save Log to export a portable copy. Browser-local storage is not a server backup.</p>
    </div>
    <div class="card">
      <div class="row"><h2>RESEARCH LOG</h2><span class="badge" id="els-count">0 entries</span></div>
      <div class="els-log" id="els-log" role="log" aria-live="polite" aria-label="External research log">
        <p class="muted">No entries yet. Research actions and notes will appear here.</p>
      </div>
      <div class="controls" style="margin-top:8px"><button id="els-clear" class="secondary">CLEAR LOCAL LOG</button></div>
      <p class="scroll-hint">Scrollable log · newest entries appear at the bottom.</p>
    </div>
  </div>
</section>

<section class="grid">
  <div class="card span-3"><h2>UNIVERSE</h2><div class="metric">PW-001</div><div class="muted">16×16 · 256 oscillators</div></div>
  <div class="card span-3"><h2>TICK</h2><div id="tick" class="metric">{tick:,}</div><div class="muted">target 100,000</div><div class="bar"><i id="progress"></i></div></div>
  <div class="card span-3"><h2>COHERENCE</h2><div id="coherence" class="metric">{coherence:.9f}</div><div class="muted">external observer measurement</div></div>
  <div class="card span-3"><h2>Ω STATUS</h2><div class="metric ok">OBSERVER</div><div class="muted">Agent Ω not activated</div></div>

  <div class="card span-6">
    <h2>LIVE OSCILLATOR FIELD · 16 × 16</h2>
    <canvas id="oscillators" width="640" height="640" aria-label="Live phase visualization of 256 oscillators"></canvas>
    <div class="legend"><span>Hue = phase (0–2π)</span><span>Arrow = phase direction</span><span id="osc-meta">Waiting for field…</span></div>
    <p class="muted" style="margin-top:8px">Live mode advances the existing universe rule and redraws the external visualization. It does not add feedback, memory, or new universe rules.</p>
  </div>

  <div class="card span-6">
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
const button=document.getElementById("step"), liveButton=document.getElementById("live");
const canvas=document.getElementById("oscillators"), ctx=canvas.getContext("2d");
const oscMeta=document.getElementById("osc-meta");

const elsLogEl=document.getElementById("els-log"), elsCountEl=document.getElementById("els-count");
const elsHypothesisEl=document.getElementById("els-hypothesis"), elsNoteEl=document.getElementById("els-note");
const ELS_STORAGE_KEY="genesis-els-0.1-log";
let elsEntries=[];
function elsPersist() {{ try {{ localStorage.setItem(ELS_STORAGE_KEY,JSON.stringify(elsEntries)); }} catch(e) {{ /* UI remains usable if storage is unavailable. */ }} }}
function elsRenderLog() {{
  elsCountEl.textContent=elsEntries.length+" entr"+(elsEntries.length===1?"y":"ies");
  elsLogEl.replaceChildren();
  if (!elsEntries.length) {{ const p=document.createElement("p"); p.className="muted"; p.textContent="No entries yet. Research actions and notes will appear here."; elsLogEl.appendChild(p); return; }}
  for (const entry of elsEntries) {{
    const article=document.createElement("article"); article.className="els-entry";
    const time=document.createElement("time"); time.dateTime=entry.timestamp; time.textContent=new Date(entry.timestamp).toLocaleString();
    const title=document.createElement("strong"); title.textContent=entry.kind;
    const body=document.createElement("div"); body.textContent=[entry.hypothesis,entry.note].filter(Boolean).join("\n");
    article.append(time,title,body); elsLogEl.appendChild(article);
  }}
  elsLogEl.scrollTop=elsLogEl.scrollHeight;
}}
function elsRecord(kind,hypothesis="",note="") {{
  elsEntries.push({{timestamp:new Date().toISOString(),kind,hypothesis,note,tick:Number(tickEl.textContent.replace(/,/g,""))||0,coherence:Number(coherenceEl.textContent)||0,layer:"ELS-0.1"}});
  elsPersist(); elsRenderLog();
}}
function elsDownload(filename,mime,text) {{
  const blob=new Blob([text],{{type:mime}}); const url=URL.createObjectURL(blob);
  const a=document.createElement("a"); a.href=url; a.download=filename; document.body.appendChild(a); a.click(); a.remove();
  setTimeout(()=>URL.revokeObjectURL(url),1000);
}}
try {{ const stored=localStorage.getItem(ELS_STORAGE_KEY); if (stored) {{ const parsed=JSON.parse(stored); if (Array.isArray(parsed)) elsEntries=parsed; }} }} catch(e) {{ elsEntries=[]; }}
elsRenderLog();
document.getElementById("els-record").addEventListener("click",()=>{{
  const hypothesis=elsHypothesisEl.value.trim(), note=elsNoteEl.value.trim();
  if (!hypothesis && !note) {{ elsNoteEl.focus(); return; }}
  elsRecord("Research note",hypothesis,note); elsNoteEl.value="";
}});
document.getElementById("els-save").addEventListener("click",()=>{{
  elsDownload("genesis-els-0.1-log.json","application/json",JSON.stringify({{schema:"GENESIS: ELS-0.1",saved_at:new Date().toISOString(),boundary:"external; no feedback into universe",entries:elsEntries}},null,2));
  elsRecord("Log exported","Saved JSON research log","Export is a UI action; the log includes this action after the exported snapshot.");
}});
document.getElementById("els-export-text").addEventListener("click",()=>{{
  const text=["GENESIS: ELS-0.1 RESEARCH LOG","Boundary: external; no feedback into GENESIS-PW-001","",...elsEntries.map(e=>`[${{e.timestamp}}] ${{e.kind}} | tick=${{e.tick}} | coherence=${{e.coherence}}\n${{e.hypothesis||""}}\n${{e.note||""}}\n`)].join("\n");
  elsDownload("genesis-els-0.1-log.txt","text/plain;charset=utf-8",text);
  elsRecord("Log exported","Saved text research log","Export is a UI action.");
}});
document.getElementById("els-clear").addEventListener("click",()=>{{
  if (!confirm("Clear the ELS-0.1 log stored in this browser? Export a copy first if you need it.")) return;
  elsEntries=[]; elsPersist(); elsRenderLog();
  elsRecord("Local log cleared","Previous local entries removed","The clear event begins a new local log.");
}});

let liveTimer=null, requestBusy=false;
function render(s) {{{{
  tickEl.textContent=Number(s.tick).toLocaleString();
  coherenceEl.textContent=Number(s.coherence).toFixed(9);
  progressEl.style.width=Math.min(100, Number(s.tick)/100000*100)+"%";
  stateEl.textContent=JSON.stringify(s);
}}}}
async function refreshOscillators() {{{{
  const response=await fetch("/oscillators", {{{{cache:"no-store"}}}});
  if (!response.ok) throw new Error("oscillator field unavailable");
  const field=await response.json();
  const phases=field.phase, n=field.size, cell=canvas.width/n;
  ctx.clearRect(0,0,canvas.width,canvas.height);
  for (let y=0;y<n;y++) for (let x=0;x<n;x++) {{{{
    const phase=phases[y][x], cx=(x+.5)*cell, cy=(y+.5)*cell;
    ctx.fillStyle=`hsl(${{{{phase/(2*Math.PI)*360}}}},72%,52%)`;
    ctx.beginPath(); ctx.arc(cx,cy,cell*.29,0,2*Math.PI); ctx.fill();
    const length=cell*.22, ex=cx+Math.cos(phase)*length, ey=cy+Math.sin(phase)*length;
    ctx.strokeStyle="#f3f7fb"; ctx.lineWidth=1.5; ctx.beginPath(); ctx.moveTo(cx,cy); ctx.lineTo(ex,ey); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(ex,ey); ctx.lineTo(ex-Math.cos(phase-.55)*cell*.09,ey-Math.sin(phase-.55)*cell*.09);
    ctx.lineTo(ex-Math.cos(phase+.55)*cell*.09,ey-Math.sin(phase+.55)*cell*.09); ctx.closePath(); ctx.fillStyle="#f3f7fb"; ctx.fill();
  }}}}
  oscMeta.textContent=`${{{{n*n}}}} oscillators · tick ${{{{field.tick}}}}`;
}}}}
async function advanceAndRender() {{{{
  if (requestBusy) return;
  requestBusy=true;
  try {{{{
    const response=await fetch("/step", {{{{cache:"no-store"}}}});
    if (!response.ok) throw new Error("step failed");
    render(await response.json());
    await refreshOscillators();
  }}}} catch (error) {{{{ oscMeta.textContent="Connection error — retrying"; }}}}
  finally {{{{ requestBusy=false; }}}}
}}}}
button.addEventListener("click", async () => {{{{
  elsRecord("Manual advance","Advanced universe by one tick","Recorded externally; no research-layer feedback.");
  button.disabled=true;
  try {{{{ await advanceAndRender(); }}}} finally {{{{ button.disabled=false; }}}}
}}}});
liveButton.addEventListener("click", () => {{{{
  if (liveTimer!==null) {{{{ clearInterval(liveTimer); liveTimer=null; liveButton.textContent="START LIVE"; liveButton.classList.add("secondary"); elsRecord("Live mode stopped"); return; }}}}
  liveButton.textContent="STOP LIVE"; liveButton.classList.remove("secondary");
  elsRecord("Live mode started","External visualization running","The research layer observes UI activity only.");
  advanceAndRender(); liveTimer=setInterval(advanceAndRender,250);
}}}});
window.addEventListener("load", async () => {{
  const response=await fetch("/state", {{cache:"no-store"}});
  if (response.ok) render(await response.json());
  try {{ await refreshOscillators(); }} catch (error) {{ oscMeta.textContent="Waiting for server…"; }}
}});
</script>
</body>
</html>"""
