"""Remotive remote-jobs aggregator API (free, no auth).

  GET https://remotive.com/api/remote-jobs?search=<kw>&limit=<n>
Returns remote roles across many companies; great for broad coverage.
"""
from __future__ import annotations

import urllib.parse
from typing import List

from ..httputil import get_json
from ..models import Job
from ..textutil import html_to_text

URL = "https://remotive.com/api/remote-jobs"


def parse(payload: dict, company: str | None = None) -> List[Job]:
    jobs: List[Job] = []
    for j in (payload or {}).get("jobs", []) or []:
        loc = (j.get("candidate_required_location", "") or "")
        jobs.append(Job(
            source="remotive",
            company=j.get("company_name", "") or "",
            title=(j.get("title") or "").strip(),
            url=j.get("url", "") or "",
            location_raw=(loc + " Remote").strip(),
            description=html_to_text(j.get("description", "")),
            salary_raw=j.get("salary", "") or "",
            posted_at=j.get("publication_date", "") or "",
            external_id=str(j.get("id", "")),
        ))
    return jobs


def fetch(search: str | None = None, limit: int = 50) -> List[Job]:
    url = f"{URL}?limit={int(limit)}"
    if search:
        url += "&search=" + urllib.parse.quote(search)
    return parse(get_json(url))
