"""Apify source adapter — runs job-scraper actors (LinkedIn, Indeed, Glassdoor)
via Apify's REST API and maps their dataset items into Job objects.

This is what extends coverage beyond company ATS boards to the big aggregators.

Requires APIFY_TOKEN in the environment (free tier works for light use).
Searches are configured in config/apify.yaml — each entry names an actor and
its input payload (input schemas differ per actor; see the actor's page).

Run-sync endpoint:
  POST https://api.apify.com/v2/acts/{actor}/run-sync-get-dataset-items?token=...
  body = the actor's input JSON
Actor ids use '~' between user and name, e.g. bebity~linkedin-jobs-scraper.
"""
from __future__ import annotations

import os
from typing import Any

import requests

from ..models import Job, strip_html, parse_comp

API = "https://api.apify.com/v2/acts/{actor}/run-sync-get-dataset-items"


def _token() -> str:
    tok = os.environ.get("APIFY_TOKEN")
    if not tok:
        raise RuntimeError("Set APIFY_TOKEN (export it or put it in a .env file).")
    return tok


def run_actor(actor: str, actor_input: dict, *, timeout: int = 300) -> list[dict]:
    """Run an Apify actor synchronously and return its dataset items."""
    url = API.format(actor=actor)
    resp = requests.post(
        url, params={"token": _token(), "timeout": timeout},
        json=actor_input, timeout=timeout + 15,
    )
    resp.raise_for_status()
    return resp.json()


# Field aliases: actors disagree on naming, so we try several per field. -----
_ALIASES: dict[str, list[str]] = {
    "title": ["title", "positionName", "jobTitle", "position"],
    "company": ["companyName", "company", "company_name", "employer"],
    "location": ["location", "jobLocation", "place", "formattedLocation"],
    "url": ["jobUrl", "url", "link", "applyUrl", "externalApplyLink", "jobPostingUrl"],
    "job_id": ["id", "jobId", "jobkey", "key"],
    "department": ["department", "function", "sector", "category"],
    "employment_type": ["employmentType", "contractType", "jobType", "workType"],
    "description": ["descriptionText", "description", "jobDescription", "descriptionHtml"],
    "posted_at": ["postedAt", "publishedAt", "postingDateParsed", "datePosted", "date"],
    "salary": ["salary", "salaryInfo", "compensation", "salaryText"],
}


def _pick(item: dict, field: str) -> str:
    for key in _ALIASES[field]:
        v = item.get(key)
        if isinstance(v, dict):
            v = v.get("name") or v.get("text") or v.get("displayName") or ""
        if v:
            return str(v)
    return ""


def _to_job(item: dict, source_label: str) -> Job | None:
    title = _pick(item, "title")
    if not title:
        return None
    desc = strip_html(_pick(item, "description"))
    loc = _pick(item, "location")
    salary_text = _pick(item, "salary")
    cmin, cmax = parse_comp(salary_text) if salary_text else parse_comp(desc)
    remote = bool(item.get("isRemote")) or "remote" in (loc + " " + _pick(item, "employment_type")).lower()
    return Job(
        source=f"apify:{source_label}",
        company=_pick(item, "company") or "(unknown)",
        title=title,
        location=loc,
        url=_pick(item, "url"),
        job_id=_pick(item, "job_id"),
        department=_pick(item, "department"),
        remote=remote,
        employment_type=_pick(item, "employment_type"),
        comp_min=cmin, comp_max=cmax,
        description=desc,
        posted_at=_pick(item, "posted_at"),
    )


def fetch_search(search: dict) -> list[Job]:
    """Run one configured search entry: {actor, label, input}."""
    actor = search["actor"]
    label = search.get("label", actor.split("~")[-1])
    items = run_actor(actor, search.get("input", {}))
    jobs = [_to_job(it, label) for it in items]
    return [j for j in jobs if j]
