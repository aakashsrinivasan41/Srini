"""Ashby public Job Board API.

Docs: https://developers.ashbyhq.com/docs/public-job-posting-api
List: GET https://api.ashbyhq.com/posting-api/job-board/{slug}?includeCompensation=true
(POST also works; GET is simpler and cache-friendly.)
"""
from __future__ import annotations

from ..models import Job, strip_html, parse_comp
from .base import get_json

BASE = "https://api.ashbyhq.com/posting-api/job-board"


def fetch(company: str, slug: str, **_: object) -> list[Job]:
    data = get_json(f"{BASE}/{slug}", params={"includeCompensation": "true"})
    out: list[Job] = []
    for j in data.get("jobs", []):
        desc = strip_html(j.get("descriptionHtml", "") or j.get("descriptionPlain", ""))
        cmin, cmax = _comp(j) or parse_comp(desc)
        loc = j.get("location", "") or ""
        out.append(Job(
            source="ashby",
            company=company,
            title=j.get("title", "").strip(),
            location=loc,
            url=j.get("jobUrl") or j.get("applyUrl", ""),
            job_id=str(j.get("id", "")),
            department=j.get("department", "") or j.get("team", ""),
            remote=bool(j.get("isRemote")) or ("remote" in loc.lower()),
            employment_type=j.get("employmentType", "") or "",
            comp_min=cmin, comp_max=cmax,
            description=desc,
            posted_at=j.get("publishedAt", "") or "",
        ))
    return out


def _comp(j: dict) -> tuple | None:
    """Pull structured compensation if Ashby exposes it."""
    comp = j.get("compensation") or {}
    summary = comp.get("compensationTierSummary") or ""
    if summary:
        from ..models import parse_comp as pc
        lo, hi = pc(summary)
        if lo:
            return lo, hi
    return None
