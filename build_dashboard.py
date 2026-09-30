"""
Generate a self-contained static dashboard (dashboard/index.html) from the DB.

The page embeds the job data as JSON and does all search / filter / sort in the
browser, so it can be opened directly (double-click) or hosted as a static site
on Render with zero backend.
"""
import json
import os
from datetime import datetime, timezone

import config
import db

_TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Job Bot — Remote USA</title>
<style>
  :root {
    --bg:#0f1115; --panel:#171a21; --border:#262b36; --text:#e6e9ef;
    --muted:#98a2b3; --accent:#4f8cff; --chip:#1f2530;
  }
  @media (prefers-color-scheme: light) {
    :root { --bg:#f6f7f9; --panel:#fff; --border:#e3e6ea; --text:#1a1d23;
            --muted:#5b6472; --accent:#2563eb; --chip:#eef1f5; }
  }
  * { box-sizing:border-box; }
  body { margin:0; font:15px/1.5 system-ui,Segoe UI,Roboto,sans-serif;
         background:var(--bg); color:var(--text); }
  header { padding:20px 16px 8px; }
  h1 { margin:0 0 4px; font-size:22px; }
  .sub { color:var(--muted); font-size:13px; }
  .controls { display:flex; flex-wrap:wrap; gap:10px; padding:12px 16px; }
  input, select { background:var(--panel); color:var(--text);
    border:1px solid var(--border); border-radius:8px; padding:8px 10px; font-size:14px; }
  #q { flex:1 1 260px; min-width:200px; }
  .stats { display:flex; flex-wrap:wrap; gap:8px; padding:0 16px 12px; }
  .chip { background:var(--chip); border:1px solid var(--border);
    border-radius:999px; padding:4px 10px; font-size:12px; color:var(--muted); }
  .wrap { padding:0 16px 40px; }
  table { width:100%; border-collapse:collapse; background:var(--panel);
    border:1px solid var(--border); border-radius:12px; overflow:hidden; }
  th, td { text-align:left; padding:10px 12px; border-bottom:1px solid var(--border);
    font-size:14px; vertical-align:top; }
  th { color:var(--muted); font-weight:600; cursor:pointer; user-select:none;
    position:sticky; top:0; background:var(--panel); }
  tr:last-child td { border-bottom:none; }
  td a { color:var(--accent); text-decoration:none; }
  td a:hover { text-decoration:underline; }
  .tag { font-size:11px; color:var(--muted); border:1px solid var(--border);
    border-radius:6px; padding:1px 6px; white-space:nowrap; }
  .empty { padding:40px; text-align:center; color:var(--muted); }
  footer { color:var(--muted); font-size:12px; padding:16px; text-align:center; }
</style>
</head>
<body>
<header>
  <h1>Job Bot — Remote USA</h1>
  <div class="sub">Software / ML / Platform / New-Grad roles · last 24h per run · Tier 1 sources</div>
</header>

<div class="stats" id="stats"></div>

<div class="controls">
  <input id="q" type="search" placeholder="Search title, company, platform…">
  <select id="platform"><option value="">All platforms</option></select>
  <select id="role"><option value="">All roles</option></select>
</div>

<div class="wrap">
  <table id="tbl">
    <thead><tr>
      <th data-k="title">Job Title</th>
      <th data-k="company">Company</th>
      <th data-k="platform">Platform</th>
      <th data-k="search_term">Role</th>
      <th data-k="location">Location</th>
      <th data-k="posted_at">Posted</th>
      <th data-k="scraped_at">Scraped</th>
    </tr></thead>
    <tbody id="rows"></tbody>
  </table>
  <div class="empty" id="empty" style="display:none">No jobs match your filters.</div>
</div>

<footer>Generated __GENERATED_AT__ · __TOTAL__ jobs in database</footer>

<script>
const JOBS = __DATA__;
const fmt = s => { if(!s) return "—"; const d=new Date(s); return isNaN(d)? "—":
  d.toLocaleString(undefined,{month:'short',day:'numeric',hour:'2-digit',minute:'2-digit'}); };

const q=document.getElementById('q'), platform=document.getElementById('platform'),
      role=document.getElementById('role'), rows=document.getElementById('rows'),
      empty=document.getElementById('empty'), stats=document.getElementById('stats');

[...new Set(JOBS.map(j=>j.platform))].sort().forEach(p=>{
  const o=document.createElement('option'); o.value=p; o.textContent=p; platform.appendChild(o); });
[...new Set(JOBS.map(j=>j.search_term))].filter(Boolean).sort().forEach(r=>{
  const o=document.createElement('option'); o.value=r; o.textContent=r; role.appendChild(o); });

const counts={}; JOBS.forEach(j=>counts[j.platform]=(counts[j.platform]||0)+1);
stats.innerHTML = `<span class="chip">Total: ${JOBS.length}</span>` +
  Object.entries(counts).sort((a,b)=>b[1]-a[1])
    .map(([p,c])=>`<span class="chip">${p}: ${c}</span>`).join('');

let sortK='scraped_at', sortDir=-1;
function render(){
  const term=q.value.toLowerCase(), pf=platform.value, rl=role.value;
  let data=JOBS.filter(j=>{
    if(pf && j.platform!==pf) return false;
    if(rl && j.search_term!==rl) return false;
    if(term){ const hay=(j.title+' '+(j.company||'')+' '+j.platform+' '+(j.location||'')).toLowerCase();
      if(!hay.includes(term)) return false; }
    return true;
  });
  data.sort((a,b)=>{ const x=(a[sortK]||''),y=(b[sortK]||''); return x<y?-sortDir:x>y?sortDir:0; });
  rows.innerHTML = data.map(j=>`<tr>
    <td><a href="${j.url}" target="_blank" rel="noopener">${esc(j.title)}</a></td>
    <td>${esc(j.company||'—')}</td>
    <td><span class="tag">${esc(j.platform)}</span></td>
    <td>${esc(j.search_term||'—')}</td>
    <td>${esc(j.location||'—')}</td>
    <td>${fmt(j.posted_at)}</td>
    <td>${fmt(j.scraped_at)}</td></tr>`).join('');
  empty.style.display = data.length? 'none':'block';
}
function esc(s){ return (s||'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c])); }
document.querySelectorAll('th').forEach(th=>th.onclick=()=>{
  const k=th.dataset.k; if(k===sortK) sortDir*=-1; else{sortK=k; sortDir=1;} render(); });
[q,platform,role].forEach(el=>el.addEventListener('input',render));
render();
</script>
</body>
</html>
"""


def build():
    os.makedirs(config.DASHBOARD_DIR, exist_ok=True)
    jobs = db.fetch_all()
    total, _ = db.stats()
    payload = [
        {
            "title": j["title"], "company": j["company"], "platform": j["platform"],
            "search_term": j["search_term"], "location": j["location"],
            "url": j["url"], "posted_at": j["posted_at"], "scraped_at": j["scraped_at"],
        }
        for j in jobs
    ]
    html = (
        _TEMPLATE
        .replace("__DATA__", json.dumps(payload))
        .replace("__GENERATED_AT__", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"))
        .replace("__TOTAL__", str(total))
    )
    with open(config.DASHBOARD_HTML, "w", encoding="utf-8") as f:
        f.write(html)
    return config.DASHBOARD_HTML


if __name__ == "__main__":
    print("Dashboard written to", build())
