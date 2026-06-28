"""Greenhouse Job Board API.

Docs: https://developers.greenhouse.io/job-board.html
List:   GET https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true
Single: GET https://boards-api.greenhouse.io/v1/boards/{slug}/jobs/{id}?questions=true
"""
from __future__ import annotations

from ..models import Job, strip_html, parse_comp
from .base import get_json

BASE = "https://boards-api.greenhouse.io/v1/boards"


def fetch(company: str, slug: str, *, with_content: bool = True) -> list[Job]:
    data = get_json(f"{BASE}/{slug}/jobs", params={"content": str(with_content).lower()})
    out: list[Job] = []
    for j in data.get("jobs", []):
        content = strip_html(j.get("content", "")) if with_content else ""
        cmin, cmax = parse_comp(content)
        loc = (j.get("location") or {}).get("name", "")
        out.append(Job(
            source="greenhouse",
            company=company,
            title=j.get("title", "").strip(),
            location=loc,
            url=j.get("absolute_url", ""),
            job_id=str(j.get("id", "")),
            department=_first_dept(j),
            remote="remote" in loc.lower(),
            comp_min=cmin, comp_max=cmax,
            description=content,
            posted_at=j.get("updated_at", "") or j.get("first_published", ""),
        ))
    return out


def fetch_questions(slug: str, job_id: str) -> list[dict]:
    """Return the application form's question definitions for a single job.

    Each entry: {label, required, fields:[{name, type, values}]}. Used by the
    autofiller to know what the form will ask before opening a browser.
    """
    data = get_json(f"{BASE}/{slug}/jobs/{job_id}", params={"questions": "true"})
    return data.get("questions", [])


def _first_dept(j: dict) -> str:
    depts = j.get("departments") or []
    return depts[0]["name"] if depts and depts[0].get("name") else ""
