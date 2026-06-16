"""Render results as a CLI table and a self-contained HTML dashboard."""
from __future__ import annotations

import html
import re
from datetime import datetime
from typing import List

from .state import row_matched, row_reasons

_BUCKET_LABEL = {"ny": "NY metro", "sf": "SF Bay", "remote": "Remote", "other": "Other"}


def _trunc(text: str, n: int) -> str:
    text = text or ""
    return text if len(text) <= n else text[: n - 1] + "…"


def cli_table(rows: List[dict], limit: int = 40) -> str:
    if not rows:
        return "No matching jobs tracked yet. Run `scan` first."
    out = []
    header = f"{'SCORE':>5}  {'NEW':<3} {'TITLE':<38} {'COMPANY':<20} {'LOC':<8} {'SALARY':<14} ID"
    out.append(header)
    out.append("-" * len(header))
    for r in rows[:limit]:
        new = "•" if r["status"] == "new" else ""
        sal = "—"
        if r.get("salary_max"):
            lo = r.get("salary_min")
            sal = f"${lo // 1000}-{r['salary_max'] // 1000}k" if lo and lo != r["salary_max"] else f"${r['salary_max'] // 1000}k"
        out.append(
            f"{r['score']:>5.1f}  {new:<3} {_trunc(r['title'], 38):<38} "
            f"{_trunc(r['company'], 20):<20} {_BUCKET_LABEL.get(r['location_bucket'], '?'):<8} "
            f"{sal:<14} {r['key']}"
        )
    if len(rows) > limit:
        out.append(f"... and {len(rows) - limit} more (see report.html)")
    return "\n".join(out)


def _row_html(r: dict) -> str:
    matched = ", ".join(row_matched(r)) or "—"
    reasons = " · ".join(row_reasons(r)) or ""
    sal = "—"
    if r.get("salary_max"):
        lo = r.get("salary_min")
        sal = f"${lo // 1000}k–${r['salary_max'] // 1000}k" if lo and lo != r["salary_max"] else f"${r['salary_max'] // 1000}k"
    ask = f"${r['suggested_ask'] // 1000}k" if r.get("suggested_ask") else "—"
    e = html.escape
    new_badge = '<span class="new">NEW</span>' if r["status"] == "new" else ""
    return f"""<tr data-bucket="{e(r['location_bucket'])}" data-status="{e(r['status'])}" data-source="{e(r['source'])}">
      <td class="score">{r['score']:.1f}</td>
      <td>{new_badge}<a href="{e(r['url'])}" target="_blank" rel="noopener">{e(r['title'])}</a>
          <div class="meta">{e(matched)}</div></td>
      <td>{e(r['company'])}</td>
      <td><span class="chip {e(r['location_bucket'])}">{e(_BUCKET_LABEL.get(r['location_bucket'], '?'))}</span>
          <div class="meta">{e(r['location_raw'])}</div></td>
      <td>{e(sal)}</td>
      <td class="ask">{e(ask)}</td>
      <td class="src">{e(r['source'])}</td>
      <td class="why">{e(reasons)}</td>
      <td class="id">{e(r['key'])}</td>
    </tr>"""


def render_html(rows: List[dict], stats: List[dict], profile_name: str) -> str:
    generated = datetime.now().strftime("%Y-%m-%d %H:%M")
    new_n = sum(1 for r in rows if r["status"] == "new")
    src_summary = " · ".join(
        f"{s['source']}: {'ERR' if s['error'] else s['count']}" for s in stats
    ) or "no sources run"
    body = "\n".join(_row_html(r) for r in rows) or '<tr><td colspan="9">No matches yet — run a scan.</td></tr>'
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Job Radar</title>
<style>
  :root {{ color-scheme: light dark; }}
  body {{ font: 14px/1.45 -apple-system, Segoe UI, Roboto, sans-serif; margin: 0; background:#0f1115; color:#e6e8ee; }}
  header {{ padding: 16px 20px; background:#161a22; border-bottom:1px solid #262b36; position:sticky; top:0; }}
  h1 {{ margin:0; font-size:18px; }}
  .sub {{ color:#9aa3b2; font-size:12px; margin-top:4px; }}
  .controls {{ padding:10px 20px; display:flex; gap:8px; flex-wrap:wrap; align-items:center; background:#11141a; border-bottom:1px solid #262b36; position:sticky; top:62px; }}
  input, select {{ background:#1b2029; color:#e6e8ee; border:1px solid #2c3340; border-radius:6px; padding:6px 8px; font-size:13px; }}
  table {{ border-collapse:collapse; width:100%; }}
  th, td {{ text-align:left; padding:8px 12px; border-bottom:1px solid #20252f; vertical-align:top; }}
  th {{ position:sticky; top:108px; background:#161a22; cursor:pointer; user-select:none; font-size:12px; color:#aeb6c4; }}
  tr:hover td {{ background:#151922; }}
  td.score {{ font-weight:700; color:#7dd3a0; }}
  a {{ color:#7aa2ff; text-decoration:none; font-weight:600; }}
  a:hover {{ text-decoration:underline; }}
  .meta {{ color:#8a93a3; font-size:11px; margin-top:2px; }}
  .why {{ color:#9aa3b2; font-size:12px; max-width:260px; }}
  .id, .src {{ color:#6b7384; font-size:11px; font-family:ui-monospace, monospace; }}
  .ask {{ color:#f3c969; font-weight:600; }}
  .new {{ background:#2c6e49; color:#fff; font-size:10px; padding:1px 5px; border-radius:4px; margin-right:6px; }}
  .chip {{ font-size:11px; padding:1px 7px; border-radius:10px; }}
  .chip.ny {{ background:#27406b; color:#bcd2ff; }}
  .chip.sf {{ background:#2c5b53; color:#bdf0e3; }}
  .chip.remote {{ background:#5b4b2c; color:#f0e4bd; }}
  .chip.other {{ background:#3a3f4a; color:#c3c9d4; }}
</style></head>
<body>
<header>
  <h1>Job Radar <span style="color:#7dd3a0">· {len(rows)} matches</span> <span style="color:#2c6e49">({new_n} new)</span></h1>
  <div class="sub">Generated {generated} · profile: {html.escape(profile_name)} · sources — {html.escape(src_summary)}</div>
</header>
<div class="controls">
  <input id="q" placeholder="filter title / company…" oninput="filt()">
  <select id="loc" onchange="filt()">
    <option value="">all locations</option><option value="ny">NY metro</option>
    <option value="sf">SF Bay</option><option value="remote">Remote</option><option value="other">Other</option>
  </select>
  <select id="st" onchange="filt()">
    <option value="">all statuses</option><option value="new">new only</option><option value="seen">seen</option>
  </select>
  <span class="sub">tip: click a column header to sort</span>
</div>
<table id="t"><thead><tr>
  <th data-k="num">Score</th><th>Title / matches</th><th>Company</th>
  <th>Location</th><th>Salary</th><th>Suggested ask</th><th>Source</th><th>Why</th><th>ID</th>
</tr></thead><tbody>
{body}
</tbody></table>
<script>
function filt() {{
  var q=document.getElementById('q').value.toLowerCase();
  var loc=document.getElementById('loc').value, st=document.getElementById('st').value;
  document.querySelectorAll('#t tbody tr').forEach(function(tr){{
    var t=tr.innerText.toLowerCase();
    var ok=(!q||t.indexOf(q)>=0)&&(!loc||tr.dataset.bucket===loc)&&(!st||tr.dataset.status===st);
    tr.style.display=ok?'':'none';
  }});
}}
document.querySelectorAll('#t th').forEach(function(th,i){{
  th.addEventListener('click',function(){{
    var tb=document.querySelector('#t tbody'),rows=[].slice.call(tb.querySelectorAll('tr'));
    var num=th.dataset.k==='num'; th._d=!th._d;
    rows.sort(function(a,b){{
      var x=a.children[i].innerText, y=b.children[i].innerText;
      if(num){{x=parseFloat(x)||0;y=parseFloat(y)||0;return th._d?x-y:y-x;}}
      return th._d?x.localeCompare(y):y.localeCompare(x);
    }});
    rows.forEach(function(r){{tb.appendChild(r);}});
  }});
}});
</script>
</body></html>"""


def slugify(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")
    return s[:50] or "job"


def _salary_line(row: dict) -> str:
    if row.get("salary_max"):
        lo = row.get("salary_min")
        sal = f"${lo // 1000}k–${row['salary_max'] // 1000}k" if lo and lo != row["salary_max"] else f"${row['salary_max'] // 1000}k"
    else:
        sal = "not listed"
    ask = f"${row['suggested_ask'] // 1000}k" if row.get("suggested_ask") else "—"
    return f"{sal} · suggested ask: {ask}"


def render_packet(row: dict, info_sheet: str, chrome_prompt: str) -> str:
    """A self-contained, paste-ready application packet for Claude-for-Chrome."""
    matched = ", ".join(row_matched(row)) or "—"
    return f"""# Application packet — {row['title']} @ {row['company']}

**Apply here:** {row['url']}

- Location: {row.get('location_raw') or '—'}  ({_BUCKET_LABEL.get(row.get('location_bucket'), '?')})
- Salary: {_salary_line(row)}
- Match score: {row.get('score', 0)} · matched: {matched}

---
## 1) Open the posting above → open the Claude side panel → paste this:

{chrome_prompt}

---
## 2) My info sheet (Claude fills fields from this)

```
{info_sheet}
```

---
## 3) This specific role
- Title:    {row['title']}
- Company:  {row['company']}
- Location: {row.get('location_raw') or '—'}
- Source:   {row.get('source', '')}
- URL:      {row['url']}
"""
