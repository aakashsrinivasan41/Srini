"""LinkedIn jobs via the public guest endpoint — no login, no paid actor.

LinkedIn's own job-search page lazy-loads cards from:
  https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search
which returns a chunk of <li> job cards as HTML. We page through it and parse
the cards. This needs no auth and includes the real posted date.

Resilience notes:
  * Markup changes occasionally. Every field is extracted by a named regex in
    SELECTORS below — if LinkedIn renames a class, inspect a card in your
    browser and update the one pattern; nothing else needs to change.
  * The endpoint rate-limits (HTTP 429). We back off and stop politely rather
    than hammering. Keep max_results modest and don't run it in a tight loop.
  * Filters map to LinkedIn's own URL params:
      f_TPR=r{seconds}  time posted range (freshness)
      f_WT=2            remote only
      geoId / location  where

This is for personal job search against a public endpoint. Be courteous:
low volume, real User-Agent, accept that some runs may be throttled.
"""
from __future__ import annotations

import html
import re
import time
from urllib.parse import urlencode

import requests

from ..models import Job, strip_html, parse_comp

GUEST = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
PER_PAGE = 25
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

# One regex per field. Update the right-hand pattern if LinkedIn changes markup.
SELECTORS = {
    "url":      re.compile(r'href="(https://www\.linkedin\.com/jobs/view/[^"?]+)'),
    "job_id":   re.compile(r'data-entity-urn="urn:li:jobPosting:(\d+)"'),
    "title":    re.compile(r'base-search-card__title">\s*(.*?)\s*</h3>', re.S),
    "company":  re.compile(r'(?:hidden-nested-link|base-search-card__subtitle)[^>]*>.*?>\s*(.*?)\s*</a>', re.S),
    "location": re.compile(r'job-search-card__location">\s*(.*?)\s*</span>', re.S),
    "date":     re.compile(r'datetime="([^"]+)"'),
}


def _get_html(params: dict, retries: int = 4) -> str:
    url = f"{GUEST}?{urlencode(params)}"
    backoff = 3.0
    for attempt in range(retries):
        r = requests.get(url, headers={"User-Agent": UA, "Accept": "text/html"}, timeout=25)
        if r.status_code == 429:                 # throttled — back off, then give up gracefully
            if attempt < retries - 1:
                time.sleep(backoff * (2 ** attempt))
                continue
            raise requests.HTTPError("429 rate-limited by LinkedIn (try again later / fewer searches)")
        if r.status_code == 400:                 # past the last page
            return ""
        r.raise_for_status()
        return r.text
    return ""


def _field(chunk: str, name: str) -> str:
    m = SELECTORS[name].search(chunk)
    return html.unescape(m.group(1)).strip() if m else ""


def _parse_cards(blob: str) -> list[dict]:
    cards = []
    for chunk in blob.split("<li>"):
        if "base-card" not in chunk and "base-search-card" not in chunk:
            continue
        title = _field(chunk, "title")
        url = _field(chunk, "url")
        if not title or not url:
            continue
        cards.append({
            "title": title,
            "url": url,
            "company": _field(chunk, "company"),
            "location": _field(chunk, "location"),
            "job_id": _field(chunk, "job_id"),
            "date": _field(chunk, "date"),
        })
    return cards


def fetch_search(search: dict) -> list[Job]:
    """Run one configured LinkedIn search and return Job objects.

    search keys: label, keywords, location, max_results, posted_within_days, remote
    """
    keywords = search.get("keywords", "")
    location = search.get("location", "United States")
    max_results = int(search.get("max_results", 75))
    label = search.get("label", "linkedin")

    base = {"keywords": keywords, "location": location}
    if search.get("posted_within_days"):
        base["f_TPR"] = f"r{int(search['posted_within_days']) * 86400}"
    if search.get("remote"):
        base["f_WT"] = "2"
    if search.get("geo_id"):
        base["geoId"] = str(search["geo_id"])

    jobs: list[Job] = []
    seen: set[str] = set()
    start = 0
    while len(jobs) < max_results:
        blob = _get_html({**base, "start": start})
        cards = _parse_cards(blob)
        if not cards:
            break
        for c in cards:
            if c["url"] in seen:
                continue
            seen.add(c["url"])
            loc = c["location"]
            jobs.append(Job(
                source=f"linkedin:{label}",
                company=c["company"] or "(unknown)",
                title=c["title"],
                location=loc,
                url=c["url"],
                job_id=c["job_id"],
                remote=bool(search.get("remote")) or "remote" in loc.lower(),
                posted_at=c["date"],
            ))
            if len(jobs) >= max_results:
                break
        start += PER_PAGE
        time.sleep(1.5)                          # be polite between pages
    return jobs
