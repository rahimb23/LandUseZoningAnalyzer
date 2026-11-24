"""Build lab/index.html: the glass, toggleable-card layout, reusing index.html's logic unchanged."""
import re, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
s = (ROOT / 'index.html').read_text()

def rep(a, b, count=1):
    global s
    n = s.count(a)
    if n != count: sys.exit(f'expected {count}, got {n}: {a[:80]!r}')
    s = s.replace(a, b)

# Data lives one folder up
rep("fetch('data/", "fetch('../data/", count=3)
# Techier mono face
rep('family=IBM+Plex+Mono:wght@400;500&', 'family=IBM+Plex+Mono:wght@400;500&family=JetBrains+Mono:wght@400;500;600&')

# ------------------------------------------------------------------ new CSS (after the existing component styles)
GLASS_CSS = r'''<style>
/* Lab layout: full-bleed map; glass cards toggled from an icon rail; HUD top right. */
:root {
  --bg: #e6ecef; --panel: #f6f9fa; --ink: #0d1c23; --muted: #4f6169; --line: rgba(13,40,55,.13);
  --accent: #0a7590; --accent-ink: #ffffff; --accent-soft: rgba(10,117,144,.13);
  --map-bg: #dbe2e5; --road: #ffffff; --road-casing: #9aabb3; --shore: #3a74a3; --poly-stroke: #ffffff;
  --ok: #1f7d4c; --warn: #a2650d; --bad: #bf3329; --unmapped: #c6d0d4;
  --glass: rgba(248,252,253,.66); --glass-strong: rgba(250,253,254,.88); --glass-line: rgba(255,255,255,.75);
  --glass-drop: rgba(10,30,40,.18); --glow: rgba(10,117,144,.22);
  --shadow: 0 10px 30px -10px var(--glass-drop);
  --f-mono: "JetBrains Mono", "IBM Plex Mono", ui-monospace, Menlo, monospace;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #060b0e; --panel: #0d151a; --ink: #e4f0f4; --muted: #8ba1ab; --line: rgba(150,210,230,.14);
    --accent: #52d6ee; --accent-ink: #03141a; --accent-soft: rgba(82,214,238,.14);
    --map-bg: #0a1115; --road: #33434c; --road-casing: #04080a; --shore: #4d93c6; --poly-stroke: #0a1115;
    --ok: #4cd18a; --warn: #f2b44a; --bad: #ff6a60; --unmapped: #223038;
    --glass: rgba(11,19,24,.6); --glass-strong: rgba(11,19,24,.84); --glass-line: rgba(150,220,240,.16);
    --glass-drop: rgba(0,0,0,.55); --glow: rgba(82,214,238,.3);
    color-scheme: dark;
  }
}
:root[data-theme="dark"] {
  --bg: #060b0e; --panel: #0d151a; --ink: #e4f0f4; --muted: #8ba1ab; --line: rgba(150,210,230,.14);
  --accent: #52d6ee; --accent-ink: #03141a; --accent-soft: rgba(82,214,238,.14);
  --map-bg: #0a1115; --road: #33434c; --road-casing: #04080a; --shore: #4d93c6; --poly-stroke: #0a1115;
  --ok: #4cd18a; --warn: #f2b44a; --bad: #ff6a60; --unmapped: #223038;
  --glass: rgba(11,19,24,.6); --glass-strong: rgba(11,19,24,.84); --glass-line: rgba(150,220,240,.16);
  --glass-drop: rgba(0,0,0,.55); --glow: rgba(82,214,238,.3);
  color-scheme: dark;
}
html, body { height: 100%; overflow: hidden; }
body { background: var(--bg); }
#map { position: fixed; inset: 0; z-index: 0; background: var(--map-bg); }

.glass {
  background: var(--glass);
  -webkit-backdrop-filter: blur(18px) saturate(160%);
  backdrop-filter: blur(18px) saturate(160%);
  border: 1px solid var(--glass-line);
  box-shadow: inset 0 1px 0 rgba(255,255,255,.08), var(--shadow);
}
@supports not ((backdrop-filter: blur(1px)) or (-webkit-backdrop-filter: blur(1px))) { .glass { background: var(--glass-strong); } }

/* Icon rail */
.rail { position: fixed; z-index: 620; left: max(12px, env(safe-area-inset-left, 0px)); top: calc(12px + env(safe-area-inset-top, 0px)); bottom: calc(12px + env(safe-area-inset-bottom, 0px));
  width: 66px; border-radius: 16px; padding: 10px 6px; display: flex; flex-direction: column; align-items: center; gap: 3px; overflow-y: auto; scrollbar-width: none; }
.rail::-webkit-scrollbar { display: none; }
.rail .logo { width: 38px; height: 38px; display: grid; place-items: center; color: var(--accent); margin-bottom: 6px; flex: none; }
.rail .grow { flex: 1; min-height: 6px; }
.rail button { all: unset; box-sizing: border-box; cursor: pointer; width: 54px; flex: none; padding: 7px 0 6px; border-radius: 11px; display: flex; flex-direction: column; align-items: center; gap: 4px;
  color: var(--muted); font: 500 9.5px/1 var(--f-mono); letter-spacing: .04em; text-transform: uppercase; transition: color .15s, background .15s, box-shadow .15s; }
.rail button svg { width: 20px; height: 20px; }
.rail button:hover { color: var(--ink); background: var(--accent-soft); }
.rail button[aria-pressed=true] { color: var(--accent); background: var(--accent-soft); box-shadow: inset 0 0 0 1px color-mix(in srgb, var(--accent) 45%, transparent), 0 0 16px -4px var(--glow); }
.rail button:focus-visible { outline: 2px solid var(--accent); outline-offset: 1px; }
.rail button[hidden] { display: none !important; }

/* Card column */
.stack-col { position: fixed; z-index: 610; left: calc(max(12px, env(safe-area-inset-left, 0px)) + 78px); top: calc(12px + env(safe-area-inset-top, 0px)); bottom: calc(12px + env(safe-area-inset-bottom, 0px));
  width: min(392px, calc(100vw - 110px)); overflow-y: auto; overscroll-behavior: contain; display: flex; flex-direction: column; gap: 10px; pointer-events: none; padding: 0 6px 0 0; scrollbar-width: thin; }
.stack-col > .card { pointer-events: auto; }
.card { border-radius: 16px; padding: 12px 14px 14px; display: flex; flex-direction: column; gap: 11px; flex: none; animation: cardIn .18s ease-out; }
.card:not(.open) { display: none; }
@keyframes cardIn { from { opacity: 0; transform: translateX(-6px); } to { opacity: 1; transform: none; } }
.card .eyebrow { font: 600 10.5px/1.2 var(--f-mono); letter-spacing: .12em; color: var(--ink); align-items: center; padding-bottom: 9px; border-bottom: 1px solid var(--line); }
.card .eyebrow .aside { margin-left: auto; font: 400 10.5px/1.2 var(--f-mono); letter-spacing: 0; color: var(--muted); text-transform: none; text-align: right; }
.card .eyebrow .t::before { content: ""; display: inline-block; width: 6px; height: 6px; border-radius: 1px; background: var(--accent); margin-right: 8px; vertical-align: 1px; box-shadow: 0 0 8px var(--glow); }
.x { all: unset; cursor: pointer; flex: none; width: 22px; height: 22px; margin-left: 6px; display: grid; place-items: center; border-radius: 6px; color: var(--muted); font: 15px/1 var(--f-body); }
.x:hover { color: var(--ink); background: var(--accent-soft); }
.x:focus-visible { outline: 2px solid var(--accent); }
.card .radius-head { border-bottom: 1px solid var(--line); padding-bottom: 9px; align-items: center; }
.card .radius-head .eyebrow { border: 0; padding: 0; }
.card .radius-head .x { margin-left: 8px; }
.radius-val { font-family: var(--f-mono); font-weight: 600; font-size: 1.6rem; letter-spacing: -.02em; }

/* Component restyle for glass */
.site, .callout, .tbl-wrap { background: color-mix(in srgb, var(--panel) 45%, transparent); border-color: var(--line); border-radius: 10px; }
.site-row { border-top-color: var(--line); }
select, .chip { background: color-mix(in srgb, var(--panel) 55%, transparent); border-color: var(--line); }
select { border-radius: 8px; }
.chip { font-family: var(--f-mono); }
.btn { border-radius: 9px; box-shadow: 0 0 18px -6px var(--glow); }
.btn.ghost { background: color-mix(in srgb, var(--panel) 30%, transparent); box-shadow: none; }
.btbl th { background: color-mix(in srgb, var(--panel) 92%, transparent); }
.sl .n, .crow .nums .pct { font-family: var(--f-mono); }
.sl .n { font-size: 1.25rem; font-weight: 600; letter-spacing: -.02em; }
.stack { height: 10px; border-radius: 5px; }
.crow { border-top-color: var(--line); }
.crow .bar { background: color-mix(in srgb, var(--ink) 8%, transparent); }
.foot { border-top: 0; padding-top: 0; }
.about h1 { margin: 0; font-family: var(--f-display); font-stretch: 85%; font-weight: 750; font-size: 1.35rem; line-height: 1.1; text-wrap: balance; }
.about p { margin: 0; font-size: .84rem; color: var(--muted); }
.legend-card ul { list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: 1fr 1fr; gap: 6px 12px; font-size: .78rem; }
.legend-card li { display: flex; gap: 7px; align-items: center; min-width: 0; }
.legend-card li small { color: var(--muted); font-family: var(--f-mono); font-size: .66rem; }

/* Top-right cluster: map switch, HUD, status, OP notice */
.tr { position: fixed; z-index: 615; top: calc(12px + env(safe-area-inset-top, 0px)); right: calc(12px + env(safe-area-inset-right, 0px)); width: min(340px, calc(100vw - 24px));
  display: flex; flex-direction: column; align-items: flex-end; gap: 8px; pointer-events: none; }
.tr > * { pointer-events: auto; }
.tr > .ov { position: static; }
.tr .toggle { border-radius: 14px; padding: 4px; background: var(--glass); }
.tr .toggle button { border-radius: 10px; font-family: var(--f-body); }
.tr .toggle button small { font-family: var(--f-mono); font-size: .64rem; }
.hud { border-radius: 14px; padding: 10px 12px; width: 100%; display: grid; grid-template-columns: auto 1fr; gap: 5px 12px; font: 400 11px/1.25 var(--f-mono); }
.hud dt { color: var(--muted); letter-spacing: .1em; text-transform: uppercase; font-size: 9.5px; padding-top: 1px; }
.hud dd { margin: 0; color: var(--ink); text-align: right; font-variant-numeric: tabular-nums; overflow-wrap: anywhere; }
.hud dd.X { color: var(--bad); } .hud dd.C { color: var(--ok); }
.hud .live { grid-column: 1 / -1; display: flex; align-items: center; gap: 6px; color: var(--muted); font-size: 9.5px; letter-spacing: .1em; text-transform: uppercase; border-bottom: 1px solid var(--line); padding-bottom: 6px; margin-bottom: 1px; }
.hud .live i { width: 7px; height: 7px; border-radius: 50%; background: var(--ok); box-shadow: 0 0 8px var(--ok); }
.hud.busy-on .live i { background: var(--warn); box-shadow: 0 0 8px var(--warn); animation: pulse 1s infinite; }
@keyframes pulse { 50% { opacity: .35; } }
.tr .busy { display: none !important; }
.tr .notice { width: 100%; border-radius: 14px; background: color-mix(in srgb, var(--warn) 10%, var(--glass)); border-color: color-mix(in srgb, var(--warn) 45%, var(--glass-line)); }
.ov.loading, .ov.empty { position: fixed; z-index: 1000; }
.ov.loading { background: var(--map-bg); font-family: var(--f-mono); letter-spacing: .04em; }
.empty { background: color-mix(in srgb, var(--map-bg) 55%, transparent); -webkit-backdrop-filter: blur(6px); backdrop-filter: blur(6px); }
.empty-card { background: var(--glass-strong); border-color: var(--glass-line); border-radius: 16px; }
.leaflet-control-zoom.leaflet-bar { border: 1px solid var(--glass-line) !important; border-radius: 12px; overflow: hidden; box-shadow: var(--shadow); }
.leaflet-bar a { background: var(--glass-strong); color: var(--ink); }
.leaflet-tooltip { background: var(--glass-strong); -webkit-backdrop-filter: blur(10px); backdrop-filter: blur(10px); border-color: var(--glass-line); border-radius: 8px; }

/* Phones: rail becomes a bottom bar; one card at a time as a bottom sheet */
@media (max-width: 760px) {
  .rail { top: auto; bottom: calc(8px + env(safe-area-inset-bottom, 0px)); left: max(8px, env(safe-area-inset-left, 0px)); right: max(8px, env(safe-area-inset-right, 0px));
    width: auto; height: 62px; flex-direction: row; padding: 5px 6px; overflow-x: auto; overflow-y: hidden; }
  .rail .logo, .rail .grow { display: none; }
  .rail button { width: 58px; }
  .stack-col { left: max(8px, env(safe-area-inset-left, 0px)); right: max(8px, env(safe-area-inset-right, 0px)); width: auto; top: auto;
    bottom: calc(78px + env(safe-area-inset-bottom, 0px)); max-height: 52vh; padding: 0; }
  .tr { top: calc(8px + env(safe-area-inset-top, 0px)); right: max(8px, env(safe-area-inset-right, 0px)); left: max(8px, env(safe-area-inset-left, 0px)); width: auto; align-items: stretch; }
  .tr .toggle { justify-content: center; }
  .tr .toggle button { flex: 1; }
  .hud { grid-template-columns: repeat(4, auto); padding: 7px 10px; gap: 2px 8px; }
  .hud .live { display: none; }
  .hud dt { font-size: 8.5px; } .hud dd { text-align: left; font-size: 10.5px; }
  .notice { top: auto; }
  .leaflet-bottom.leaflet-right { bottom: calc(76px + env(safe-area-inset-bottom, 0px)); }
}
@media (prefers-reduced-motion: reduce) { .card { animation: none; } .hud.busy-on .live i { animation: none; } }
</style>
'''
rep('<style>body{margin:0}</style>', GLASS_CSS + '<style>body{margin:0}</style>')
rep('<title>Land Use Compatibility Analysis</title>', '<title>Land Use Compatibility Lab</title>')

# ------------------------------------------------------------------ new body layout (same element ids)
i = s.index('<div class="app">'); j = s.index('<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/')
old = s[i:j]
def grab(start, end):
    a = old.index(start); b = old.index(end, a) + len(end)
    return old[a:b]
X = '<button class="x" type="button" aria-label="Close panel" data-close>×</button>'

ICONS = {
 'site': '<circle cx="10" cy="10" r="3"/><path d="M10 1.5v4M10 14.5v4M1.5 10h4M14.5 10h4"/>',
 'batch': '<circle cx="5" cy="6" r="2"/><circle cx="14.5" cy="5" r="2"/><circle cx="9" cy="14.5" r="2"/><path d="M6.6 7.4l1.4 5M13.3 6.6l-3 6.4"/>',
 'radius': '<circle cx="10" cy="10" r="8"/><circle cx="10" cy="10" r="4.5" stroke-dasharray="2 2"/><circle cx="10" cy="10" r="1" fill="currentColor"/>',
 'compat': '<path d="M3 14a7 7 0 0 1 14 0"/><path d="M10 14l3.5-4.5"/><path d="M3 17h14"/>',
 'land': '<rect x="2.5" y="3" width="15" height="3.2" rx="1"/><rect x="2.5" y="8.4" width="10" height="3.2" rx="1"/><rect x="2.5" y="13.8" width="6" height="3.2" rx="1"/>',
 'sides': '<circle cx="10" cy="10" r="8"/><path d="M10 4l2 6-2 6-2-6z"/>',
 'op': '<path d="M10 2.5l7.5 4-7.5 4-7.5-4z"/><path d="M2.5 10.5l7.5 4 7.5-4"/><path d="M2.5 14l7.5 4 7.5-4"/>',
 'legend': '<rect x="2.5" y="3.5" width="4" height="4" rx="1"/><rect x="2.5" y="12.5" width="4" height="4" rx="1"/><path d="M9.5 5.5h8M9.5 14.5h8"/>',
 'report': '<rect x="4" y="3" width="12" height="15" rx="2"/><path d="M7.5 3V1.8h5V3M7 8h6M7 11.5h6M7 15h3.5"/>',
 'about': '<circle cx="10" cy="10" r="8"/><path d="M10 9v5M10 6.2v.1"/>',
}
def ico(k): return f'<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[k]}</svg>'
RAIL = [('cardSite','site','Site'),('batchSec','batch','Sites'),('cardRadius','radius','Radius'),('cardCompat','compat','Compat'),
        ('cardComp','land','Land use'),('cardDir','sides','Sides'),('opLayerSec','op','OP layer'),('legend','legend','Legend'),('cardReport','report','Report')]
rail = '<nav class="rail glass" aria-label="Panels">\n  <div class="logo" title="Land Use Compatibility Lab"><svg viewBox="0 0 32 32" width="30" height="30" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><circle cx="16" cy="16" r="13" stroke-dasharray="3 3"/><circle cx="16" cy="16" r="7.5"/><circle cx="16" cy="16" r="2" fill="currentColor"/><path d="M16 1v5M16 26v5M1 16h5M26 16h5"/></svg></div>\n'
for cid, k, label in RAIL:
    rail += f'  <button type="button" data-card="{cid}" aria-controls="{cid}" aria-pressed="false">{ico(k)}<span>{label}</span></button>\n'
rail += f'  <div class="grow"></div>\n  <button type="button" data-card="cardAbout" aria-controls="cardAbout" aria-pressed="false">{ico("about")}<span>About</span></button>\n</nav>\n'

def hdr(title, aside=''):
    return f'<div class="eyebrow"><span class="t">{title}</span>{aside}{X}</div>'

site = f'''  <section class="card glass" id="cardSite" aria-label="Subject site">
    <div class="eyebrow" id="h-site"><span class="t">Subject site</span><span class="aside mono" id="siteCoord"></span>{X}</div>
    <div class="site" id="siteCard"></div>
    <select id="preset" aria-label="Jump to an example site"></select>
  </section>
'''
batch = grab('<section class="sec batch-drop" id="batchSec"', '</section>')
batch = batch.replace('<section class="sec batch-drop" id="batchSec" aria-labelledby="h-batch">', '<section class="card glass batch-drop" id="batchSec" aria-labelledby="h-batch">')
batch = batch.replace('<div class="eyebrow" id="h-batch">Multiple sites <span class="aside" id="batchMeta"></span></div>',
                      f'<div class="eyebrow" id="h-batch"><span class="t">Multiple sites</span><span class="aside" id="batchMeta"></span>{X}</div>')
radius = f'''  <section class="card glass" id="cardRadius" aria-labelledby="h-rad">
    <div class="radius-head">
      <div class="eyebrow" id="h-rad"><span class="t">Study radius</span></div>
      <div style="display:flex;align-items:center"><div class="radius-val mono" id="radiusVal">500<span>m</span></div>{X}</div>
    </div>
    <input type="range" id="radius" min="50" max="1500" step="10" value="500" aria-labelledby="h-rad">
    <div class="chips" id="chips"></div>
  </section>
'''
compat = grab('<section class="sec" aria-labelledby="h-eval">', '</section>')
compat = compat.replace('<section class="sec" aria-labelledby="h-eval">', '<section class="card glass" id="cardCompat" aria-labelledby="h-eval">')
compat = compat.replace('<div class="eyebrow" id="h-eval">Compatibility <span class="aside" id="areaNote"></span></div>',
                        f'<div class="eyebrow" id="h-eval"><span class="t">Compatibility</span><span class="aside" id="areaNote"></span>{X}</div>')
comp = grab('<section class="sec" aria-labelledby="h-comp">', '</section>')
comp = comp.replace('<section class="sec" aria-labelledby="h-comp">', '<section class="card glass" id="cardComp" aria-labelledby="h-comp">')
comp = comp.replace('<div class="eyebrow" id="h-comp">Surrounding land use <span class="aside" id="compSrc"></span></div>',
                    f'<div class="eyebrow" id="h-comp"><span class="t">Surrounding land use</span><span class="aside" id="compSrc"></span>{X}</div>')
sides = grab('<section class="sec" aria-labelledby="h-dir">', '</section>')
sides = sides.replace('<section class="sec" aria-labelledby="h-dir">', '<section class="card glass" id="cardDir" aria-labelledby="h-dir">')
sides = sides.replace('<div class="eyebrow" id="h-dir">What lies on each side</div>', f'<div class="eyebrow" id="h-dir"><span class="t">What lies on each side</span>{X}</div>')
oplayer = grab('<section class="sec" id="opLayerSec"', '</section>')
oplayer = oplayer.replace('<section class="sec" id="opLayerSec" hidden aria-labelledby="h-op">', '<section class="card glass" id="opLayerSec" hidden aria-labelledby="h-op">')
oplayer = oplayer.replace('<div class="eyebrow" id="h-op">Official Plan layer</div>', f'<div class="eyebrow" id="h-op"><span class="t">Official Plan layer</span>{X}</div>')
legend = f'''  <section class="card glass legend-card" id="legend" aria-labelledby="legendTitle">
    <div class="eyebrow"><span class="t" id="legendTitle">Legend</span>{X}</div>
    <ul id="legendList"></ul>
  </section>
'''
copy_btns = grab('<div class="btns">\n      <button class="btn" id="copyBtn"', '</div>')
fallback = grab('<textarea id="copyFallback"', '</textarea>')
report = f'''  <section class="card glass" id="cardReport" aria-labelledby="h-rep">
    <div class="eyebrow" id="h-rep"><span class="t">Report</span>{X}</div>
    <p class="hint" style="margin:0">Copies the site, its designations, the land use breakdown and the compatibility result as plain text for a planning report.</p>
    {copy_btns}
    {fallback}
  </section>
'''
foot = grab('<footer class="foot">', '</footer>')
about = f'''  <section class="card glass about" id="cardAbout" aria-labelledby="h-about">
    <div class="eyebrow" id="h-about"><span class="t">About</span>{X}</div>
    <h1>Land Use Compatibility Analysis</h1>
    <p>Click the map to place a site. The tool clips each land use polygon to the radius and measures what surrounds the site. Open and close panels from the rail.</p>
    <p>This is the experimental layout. <a href="../">Open the classic layout</a>.</p>
    {foot}
  </section>
'''
stack = '<div class="stack-col" id="stackCol">\n' + site + '  ' + batch + '\n' + radius + '  ' + compat + '\n  ' + comp + '\n  ' + sides + '\n  ' + oplayer + '\n' + legend + report + about + '</div>\n'

toggle = grab('<div class="ov toggle"', '</div>').replace('class="ov toggle"', 'class="ov toggle glass"')
notice = grab('<div class="ov notice"', '</div>').replace('class="ov notice"', 'class="ov notice glass"')
busy = grab('<div class="ov busy"', '</div>')
tr = f'''<div class="tr">
  {toggle}
  <dl class="hud glass" id="hud" aria-live="polite">
    <div class="live"><i></i><span id="hudState">Ready</span></div>
    <dt>Site</dt><dd id="hudSite">—</dd>
    <dt>Radius</dt><dd id="hudR">—</dd>
    <dt>Map</dt><dd id="hudMap">—</dd>
    <dt>Conflict</dt><dd id="hudX">—</dd>
  </dl>
  {busy}
  {notice}
</div>
'''
overlays = grab('<div class="ov loading" id="opLoading"', '</div>') + '\n' + grab('<div class="ov empty" id="opEmpty"', '<div class="ov loading" id="loading">').rsplit('<div class="ov loading" id="loading">', 1)[0] + grab('<div class="ov loading" id="loading">', '</div>')
new_body = '<div id="map" aria-label="Land use map"></div>\n' + rail + stack + tr + overlays + '\n\n'
s = s[:i] + new_body + s[j:]

# ------------------------------------------------------------------ rail + HUD behaviour (separate script, reads only the DOM)
UI_JS = r'''<script>
(() => {
  const KEY = 'luca-lab-cards';
  const DEFAULT = ['cardSite', 'cardRadius', 'cardCompat', 'cardComp'];
  const narrow = matchMedia('(max-width: 760px)');
  const buttons = [...document.querySelectorAll('.rail [data-card]')];
  const load = () => { try { const v = JSON.parse(localStorage.getItem(KEY)); return Array.isArray(v) ? v : null; } catch (e) { return null; } };
  const save = () => { try { localStorage.setItem(KEY, JSON.stringify(buttons.filter(b => b.getAttribute('aria-pressed') === 'true').map(b => b.dataset.card))); } catch (e) {} };
  function setOpen(id, on, scroll) {
    const el = document.getElementById(id), btn = buttons.find(b => b.dataset.card === id);
    if (!el || !btn) return;
    if (on && narrow.matches) buttons.forEach(b => { if (b !== btn && b.getAttribute('aria-pressed') === 'true') setOpen(b.dataset.card, false); });
    el.classList.toggle('open', on);
    btn.setAttribute('aria-pressed', on);
    if (on && scroll) requestAnimationFrame(() => el.scrollIntoView({ block: 'nearest', behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' }));
  }
  let initial = load() || DEFAULT;
  if (narrow.matches) initial = initial.slice(0, 1);
  initial.forEach(id => setOpen(id, true));
  buttons.forEach(b => b.addEventListener('click', () => { setOpen(b.dataset.card, b.getAttribute('aria-pressed') !== 'true', true); save(); }));
  document.querySelectorAll('[data-close]').forEach(x => x.addEventListener('click', () => { const c = x.closest('.card'); if (c) { setOpen(c.id, false); save(); } }));
  // Upload and select actions bring their panel forward
  document.getElementById('batchInput').addEventListener('change', () => setOpen('batchSec', true, true));
  // The OP layer panel only applies on the Official Plan map
  const opSec = document.getElementById('opLayerSec'), opBtn = buttons.find(b => b.dataset.card === 'opLayerSec');
  const syncOp = () => { opBtn.hidden = opSec.hidden; };
  new MutationObserver(syncOp).observe(opSec, { attributes: true, attributeFilter: ['hidden'] }); syncOp();
  // HUD mirrors the analysis
  const $ = id => document.getElementById(id);
  function hud() {
    const coord = $('siteCoord').textContent.trim();
    $('hudSite').textContent = coord || '—';
    $('hudR').textContent = $('radiusVal').textContent.replace(/\s*m$/, '') + ' m';
    $('hudMap').textContent = $('tOp').getAttribute('aria-pressed') === 'true' ? 'Official Plan' : 'Zoning';
    const x = document.querySelector('#stackLegend .c-X');
    const v = x ? x.textContent.trim() : '—';
    $('hudX').textContent = v; $('hudX').className = !x ? '' : parseFloat(v) > 0 ? 'X' : 'C';
    const busy = !$('busy').hidden || !$('loading').hidden;
    $('hud').classList.toggle('busy-on', busy);
    $('hudState').textContent = !$('loading').hidden ? 'Loading city data' : busy ? 'Measuring' : 'Live';
  }
  const mo = new MutationObserver(hud);
  ['siteCoord', 'radiusVal', 'stackLegend', 'tOp', 'busy', 'loading'].forEach(id => mo.observe($(id), { attributes: true, childList: true, characterData: true, subtree: true }));
  hud();
})();
</script>
'''
rep('</body>', UI_JS + '</body>')
(ROOT / 'lab').mkdir(exist_ok=True)
(ROOT / 'lab' / 'index.html').write_text(s)
print('lab/index.html written,', len(s), 'bytes')
