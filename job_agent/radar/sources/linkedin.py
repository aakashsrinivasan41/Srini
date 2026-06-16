"""LinkedIn — public 'guest' job-search endpoint (NO login required).

⚠️  IMPORTANT — read before enabling:
    LinkedIn's User Agreement prohibits automated access. This adapter uses ONLY
    the public, unauthenticated guest endpoint (the same job cards a logged-out
    visitor sees), at LOW VOLUME with polite delays, for DISCOVERY ONLY. It never
    logs in, never sends cookies/credentials, and never applies to anything.
    It is DISABLED by default in config/sources.yaml — enable at your own
    discretion, and apply to every role by hand.

The guest list view exposes title / company / location / link / post-date only
(no description or salary), so salary & experience filters simply don't apply to
LinkedIn rows — they're ranked on title/keyword match and location.
"""
from __future__ import annotations

import random
import re
import time
import urllib.parse
from typing import List

from ..httputil import BROWSER_UA, get_text
from ..models import Job
from ..textutil import html_to_text

SEARCH_URL = (
    "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
    "?keywords={kw}&location={loc}&f_TPR=r{tpr}&f_E={exp}&start={start}"
)
_PAGE_SIZE = 25

_CARD_RE = re.compile(r"<li\b.*?</li>", re.S)
_TITLE_RE = re.compile(r'base-search-card__title">(.*?)</h3>', re.S)
_COMPANY_A_RE = re.compile(r'base-search-card__subtitle"[^>]*>.*?<a[^>]*>(.*?)</a>', re.S)
_COMPANY_RE = re.compile(r'base-search-card__subtitle"[^>]*>(.*?)</h4>', re.S)
_LOC_RE = re.compile(r'job-search-card__location">(.*?)</span>', re.S)
_LINK_RE = re.compile(r'href="(https://www\.linkedin\.com/jobs/view/[^"?]+)', re.S)
_DATE_RE = re.compile(r'datetime="([^"]+)"')
_ID_RE = re.compile(r"(\d+)/?$")


def parse_html(html_str: str) -> List[Job]:
    jobs: List[Job] = []
    for card in _CARD_RE.findall(html_str or ""):
        link_m = _LINK_RE.search(card)
        title_m = _TITLE_RE.search(card)
        if not link_m or not title_m:
            continue
        comp_m = _COMPANY_A_RE.search(card) or _COMPANY_RE.search(card)
        loc_m = _LOC_RE.search(card)
        date_m = _DATE_RE.search(card)
        url = link_m.group(1).strip()
        id_m = _ID_RE.search(url)
        jobs.append(Job(
            source="linkedin",
            company=html_to_text(comp_m.group(1)) if comp_m else "",
            title=html_to_text(title_m.group(1)),
            url=url,
            location_raw=html_to_text(loc_m.group(1)) if loc_m else "",
            posted_at=date_m.group(1) if date_m else "",
            external_id=id_m.group(1) if id_m else "",
        ))
    return jobs


def fetch(keywords: str, location: str, experience: str = "2,3",
          posted_within_days: int = 7, pages: int = 1,
          min_delay: float = 3.0, max_delay: float = 7.0) -> List[Job]:
    tpr = int(posted_within_days) * 86400
    exp = urllib.parse.quote(str(experience))
    headers = {"User-Agent": BROWSER_UA, "Accept": "text/html"}
    out: List[Job] = []
    for page in range(max(1, int(pages))):
        url = SEARCH_URL.format(
            kw=urllib.parse.quote(keywords), loc=urllib.parse.quote(location),
            tpr=tpr, exp=exp, start=page * _PAGE_SIZE,
        )
        found = parse_html(get_text(url, headers=headers))
        out.extend(found)
        if not found:
            break
        if page < pages - 1:
            # jittered pause between pages — no fixed, robotic cadence
            time.sleep(random.uniform(max(0.0, min_delay), max(min_delay, max_delay)))
    return out
