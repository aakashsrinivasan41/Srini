"""Lever Postings API.

Docs: https://github.com/lever/postings-api
List: GET https://api.lever.co/v0/postings/{slug}?mode=json
"""
from __future__ import annotations

from ..models import Job, parse_comp
from .base import get_json

BASE = "https://api.lever.co/v0/postings"


def fetch(company: str, slug: str, **_: object) -> list[Job]:
    data = get_json(f"{BASE}/{slug}", params={"mode": "json"})
    out: list[Job] = []
    for j in data:
        cats = j.get("categories") or {}
        loc = cats.get("location", "") or ""
        desc = j.get("descriptionPlain", "") or ""
        cmin, cmax = parse_comp(desc)
        commitment = (cats.get("commitment") or "").lower()
        wp = (j.get("workplaceType") or "").lower()  # remote | on-site | hybrid
        out.append(Job(
            source="lever",
            company=company,
            title=j.get("text", "").strip(),
            location=loc,
            url=j.get("hostedUrl") or j.get("applyUrl", ""),
            job_id=str(j.get("id", "")),
            department=cats.get("team", "") or cats.get("department", ""),
            remote=("remote" in wp) or ("remote" in loc.lower()),
            employment_type=commitment,
            comp_min=cmin, comp_max=cmax,
            description=desc,
            posted_at=str(j.get("createdAt", "")),
        ))
    return out
