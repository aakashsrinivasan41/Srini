"""Render a ranked job list as a clickable, self-contained HTML page."""
from __future__ import annotations

import html
from pathlib import Path

from .models import Job, DATA_DIR, business_age_days


def _age_cell(j: Job) -> tuple[str, str]:
    """Return (label, color) for a posting's BUSINESS-day age."""
    d = business_age_days(j.posted_at)
    if d is None:
        return "?", "#9ca3af"
    label = f"{d}D"
    color = "#16a34a" if d <= 3 else "#ca8a04" if d <= 5 else "#dc2626"
    return label, color


def _score_color(s: float) -> str:
    if s >= 90:
        return "#16a34a"   # green
    if s >= 75:
        return "#65a30d"   # lime
    if s >= 60:
        return "#ca8a04"   # amber
    return "#9ca3af"        # gray


def _comp(j: Job) -> str:
    if not j.comp_min:
        return "—"
    if j.comp_max and j.comp_max != j.comp_min:
        return f"${j.comp_min//1000}k–${j.comp_max//1000}k"
    return f"${j.comp_min//1000}k"


def write_html(jobs: list[Job], path: Path | None = None, title: str = "jobhunt shortlist") -> Path:
    path = path or (DATA_DIR / "ranked.html")
    rows = []
    for i, j in enumerate(jobs):
        why = "  •  ".join(f"{k}: {html.escape(str(v))}" for k, v in j.score_breakdown.items())
        link = (f'<a href="{html.escape(j.url)}" target="_blank" rel="noopener">'
                f'{html.escape(j.title)} ↗</a>') if j.url else html.escape(j.title)
        remote = "🏠 remote" if j.remote else ""
        age_label, age_color = _age_cell(j)
        rows.append(f"""
        <tr title="{html.escape(why)}">
          <td class="idx">{i}</td>
          <td><span class="score" style="background:{_score_color(j.score)}">{j.score:g}</span></td>
          <td class="co">{html.escape(j.company)}</td>
          <td class="title">{link}</td>
          <td>{html.escape(j.location)}</td>
          <td>{remote}</td>
          <td>{_comp(j)}</td>
          <td style="color:{age_color};font-weight:600;white-space:nowrap">{age_label}</td>
          <td class="src">{html.escape(j.source)}</td>
        </tr>""")

    doc = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<style>
  :root {{ color-scheme: light dark; }}
  body {{ font: 15px/1.5 -apple-system, system-ui, sans-serif; margin: 24px; }}
  h1 {{ font-size: 20px; margin: 0 0 4px; }}
  .sub {{ color: #6b7280; margin: 0 0 16px; }}
  table {{ border-collapse: collapse; width: 100%; }}
  th, td {{ text-align: left; padding: 8px 10px; border-bottom: 1px solid #e5e7eb33; }}
  th {{ font-size: 12px; text-transform: uppercase; letter-spacing: .04em; color: #6b7280; }}
  tr:hover {{ background: #88888814; }}
  .idx {{ color: #9ca3af; width: 28px; }}
  .score {{ color: #fff; font-weight: 600; padding: 2px 8px; border-radius: 999px; font-size: 13px; }}
  .co {{ font-weight: 600; white-space: nowrap; }}
  .title a {{ color: #2563eb; text-decoration: none; font-weight: 500; }}
  .title a:hover {{ text-decoration: underline; }}
  .src {{ color: #9ca3af; font-size: 12px; }}
  td[title] {{ cursor: help; }}
</style></head>
<body>
  <h1>{html.escape(title)}</h1>
  <p class="sub">{len(jobs)} roles, ranked. Click a title to open its application. Hover a row to see why it scored.</p>
  <table>
    <thead><tr>
      <th>#</th><th>Score</th><th>Company</th><th>Title</th>
      <th>Location</th><th></th><th>Comp</th><th>Posted</th><th>Source</th>
    </tr></thead>
    <tbody>{''.join(rows)}</tbody>
  </table>
</body></html>"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(doc, encoding="utf-8")
    return path
