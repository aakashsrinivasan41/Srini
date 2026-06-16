"""Ashby public job board posting API.

  GET https://api.ashbyhq.com/posting-api/job-board/{org}?includeCompensation=true
Find {org}: their careers page at jobs.ashbyhq.com/<org>.
"""
from __future__ import annotations

from typing import List

from ..httputil import get_json
from ..models import Job
from ..textutil import html_to_text

URL = "https://api.ashbyhq.com/posting-api/job-board/{org}?includeCompensation=true"


def parse(payload: dict, company: str) -> List[Job]:
    jobs: List[Job] = []
    for j in (payload or {}).get("jobs", []) or []:
        if j.get("isListed") is False:
            continue
        location = j.get("location", "") or ""
        if j.get("isRemote"):
            location = (location + " Remote").strip()
        comp = ((j.get("compensation") or {}).get("compensationTierSummary") or "")
        desc = j.get("descriptionPlain") or html_to_text(
            j.get("descriptionHtml") or j.get("description") or ""
        )
        jobs.append(Job(
            source="ashby",
            company=company,
            title=(j.get("title") or "").strip(),
            url=j.get("jobUrl") or j.get("applyUrl", "") or "",
            location_raw=location,
            description=desc,
            salary_raw=comp,
            posted_at=j.get("publishedAt") or j.get("updatedAt", "") or "",
            external_id=str(j.get("id", "")),
        ))
    return jobs


def fetch(org: str, company: str | None = None) -> List[Job]:
    payload = get_json(URL.format(org=org))
    return parse(payload, company or org)
