"""Lever public postings API.

  GET https://api.lever.co/v0/postings/{site}?mode=json   (returns a JSON array)
Find {site}: their careers page at jobs.lever.co/<site>.
"""
from __future__ import annotations

from typing import List

from ..httputil import get_json
from ..models import Job
from ..textutil import html_to_text

URL = "https://api.lever.co/v0/postings/{site}?mode=json"


def parse(payload: list, company: str) -> List[Job]:
    jobs: List[Job] = []
    for j in payload or []:
        cats = j.get("categories") or {}
        desc = j.get("descriptionPlain") or html_to_text(j.get("description", ""))
        jobs.append(Job(
            source="lever",
            company=company,
            title=(j.get("text") or "").strip(),
            url=j.get("hostedUrl") or j.get("applyUrl", "") or "",
            location_raw=cats.get("location", "") or "",
            description=desc,
            posted_at=str(j.get("createdAt", "") or ""),
            external_id=str(j.get("id", "")),
        ))
    return jobs


def fetch(site: str, company: str | None = None) -> List[Job]:
    payload = get_json(URL.format(site=site))
    return parse(payload, company or site)
