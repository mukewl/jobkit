"""Render the job queue to a single self-contained HTML page.

No build step, no framework, no external requests. Open it from disk, or commit
public/ and let a static host serve it.

Checkbox state lives in the browser's localStorage, so it is per-device. Pick one
place to track and use it consistently.
"""
from __future__ import annotations

import html
import json
from collections import Counter
from datetime import datetime

CSS = """
:root{--bg:#faf9f7;--fg:#1a1a1a;--mut:#6b6b6b;--line:#e3e0db;--card:#fff;--acc:#c2410c}
@media(prefers-color-scheme:dark){:root{--bg:#17181a;--fg:#ececec;--mut:#9b9b9b;--line:#2e3033;--card:#1f2124;--acc:#fb923c}}
*{box-sizing:border-box}
body{margin:0;padding:2rem 1rem 4rem;background:var(--bg);color:var(--fg);
 font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
.wrap{max-width:1100px;margin:0 auto}
h1{font-size:1.6rem;margin:0 0 .25rem}
.sub{color:var(--mut);margin:0 0 1.5rem;font-size:.9rem}
.stats{display:flex;flex-wrap:wrap;gap:.5rem;margin-bottom:1.5rem}
.pill{background:var(--card);border:1px solid var(--line);border-radius:999px;
 padding:.3rem .8rem;font-size:.82rem;color:var(--mut)}
.pill b{color:var(--fg)}
table{width:100%;border-collapse:collapse;background:var(--card);
 border:1px solid var(--line);border-radius:10px;overflow:hidden}
th,td{text-align:left;padding:.6rem .7rem;border-bottom:1px solid var(--line);
 font-size:.88rem;vertical-align:top}
th{background:transparent;color:var(--mut);font-weight:600;font-size:.76rem;
 text-transform:uppercase;letter-spacing:.04em}
tr:last-child td{border-bottom:none}
tr.done{opacity:.4}
a{color:var(--acc);text-decoration:none}
a:hover{text-decoration:underline}
.fam{font-size:.72rem;color:var(--mut);border:1px solid var(--line);
 border-radius:4px;padding:.1rem .35rem;white-space:nowrap}
.scroll{overflow-x:auto}
footer{margin-top:2rem;color:var(--mut);font-size:.8rem}
"""

JS = """
const KEY='jobkit.done';
const done=new Set(JSON.parse(localStorage.getItem(KEY)||'[]'));
function paint(){
  document.querySelectorAll('tr[data-key]').forEach(tr=>{
    const on=done.has(tr.dataset.key);
    tr.classList.toggle('done',on);
    tr.querySelector('input').checked=on;
  });
  document.getElementById('n-done').textContent=done.size;
}
document.addEventListener('change',e=>{
  if(e.target.type!=='checkbox')return;
  const k=e.target.closest('tr').dataset.key;
  e.target.checked?done.add(k):done.delete(k);
  localStorage.setItem(KEY,JSON.stringify([...done]));
  paint();
});
paint();
"""


def _row(j: dict) -> str:
    e = html.escape
    title = e(j.get("title", ""))
    url = j.get("url") or ""
    link = f'<a href="{e(url)}" target="_blank" rel="noopener">{title}</a>' if url else title
    fam = j.get("family") or j.get("source") or ""
    return (
        f'<tr data-key="{e(j.get("key",""))}">'
        f'<td><input type="checkbox" aria-label="applied"></td>'
        f"<td>{link}</td>"
        f'<td>{e(j.get("company",""))}</td>'
        f'<td>{e(j.get("location",""))}</td>'
        f'<td><span class="fam">{e(fam)}</span></td>'
        f'<td>{e(j.get("posted_at") or j.get("fetched",""))}</td>'
        "</tr>"
    )


def render(jobs: list[dict], config: dict) -> str:
    jobs = sorted(jobs, key=lambda j: (j.get("fetched", ""), j.get("posted_at", "")),
                  reverse=True)
    by_family = Counter(j.get("family") or j.get("source") or "other" for j in jobs)
    pills = "".join(
        f'<span class="pill">{html.escape(k)} <b>{v}</b></span>'
        for k, v in by_family.most_common()
    )
    rows = "\n".join(_row(j) for j in jobs) or (
        '<tr><td colspan="6" style="color:var(--mut)">Nothing yet. '
        'Run <code>python search/fetch_jobs.py</code>.</td></tr>'
    )
    built = datetime.now().strftime("%d %b %Y, %H:%M")
    days = config.get("dashboard_days", 7)

    try:
        import sources
        credits = sources.attributions(j.get("source", "") for j in jobs)
    except Exception:
        credits = []
    credit_html = (" " + " ".join(credits)) if credits else ""

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Job queue</title><style>{CSS}</style></head>
<body><div class="wrap">
<h1>Job queue</h1>
<p class="sub">Last {days} days · built {built} · {len(jobs)} open ·
<span id="n-done">0</span> marked done</p>
<div class="stats"><span class="pill">total <b>{len(jobs)}</b></span>{pills}</div>
<div class="scroll"><table>
<thead><tr><th></th><th>Role</th><th>Company</th><th>Location</th><th>Family</th><th>Posted</th></tr></thead>
<tbody>
{rows}
</tbody></table></div>
<footer>Checkbox state is stored in this browser only. Built by jobkit.{credit_html}</footer>
</div><script>{JS}</script></body></html>"""
