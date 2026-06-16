"""Greenhouse public job board API.

  GET https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true
Find a company's {token}: their careers page at boards.greenhouse.io/<token>.
"""
from __future__ import annotations

from typing import List

from ..httputil import get_json
from ..models import Job
from ..textutil import html_to_text

URL = "https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true"


def parse(payload: dict, company: str) -> List[Job]:
    jobs: List[Job] = []
    for j in (payload or {}).get("jobs", []) or []:
        location = (j.get("location") or {}).get("name", "") or ""
        jobs.append(Job(
            source="greenhouse",
            company=company,
            title=(j.get("title") or "").strip(),
            url=j.get("absolute_url", "") or "",
            location_raw=location,
            description=html_to_text(j.get("content", "")),
            posted_at=j.get("updated_at", "") or "",
            external_id=str(j.get("id", "")),
        ))
    return jobs


def fetch(token: str, company: str | None = None) -> List[Job]:
    payload = get_json(URL.format(token=token))
    return parse(payload, company or token)
