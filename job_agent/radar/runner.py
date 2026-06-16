"""Fetch jobs from every configured source, isolating per-source failures."""
from __future__ import annotations

import random
import re
import time
from typing import List, Tuple

from .httputil import FetchError
from .models import Job
from .profile import Profile
from .sources import ashby, greenhouse, lever, linkedin, remotive

_SUFFIX_RE = re.compile(r"\b(inc|llc|ltd|corp|co|the|plc|gmbh)\b")


def _norm(text: str) -> str:
    text = re.sub(r"[^a-z0-9 ]", " ", (text or "").lower())
    text = _SUFFIX_RE.sub(" ", text)
    return re.sub(r"\s+", " ", text).strip()


def _dedupe(jobs: List[Job]) -> List[Job]:
    """1) drop exact URL duplicates; 2) drop a LinkedIn row when the same
    company+title already exists from an ATS/aggregator (those links are
    richer — direct apply + description/salary)."""
    seen, url_unique = set(), []
    for job in jobs:
        if not job.title or not job.url or job.key in seen:
            continue
        seen.add(job.key)
        url_unique.append(job)
    ats_pairs = {
        (_norm(j.company), _norm(j.title))
        for j in url_unique if j.source != "linkedin"
    }
    return [
        j for j in url_unique
        if not (j.source == "linkedin" and (_norm(j.company), _norm(j.title)) in ats_pairs)
    ]


def collect(sources_cfg: dict, profile: Profile) -> Tuple[List[Job], List[dict]]:
    """Returns (jobs, stats). `stats` has one entry per source attempt so the
    CLI can report exactly what worked and what didn't."""
    jobs: List[Job] = []
    stats: List[dict] = []

    def _run(label: str, fn):
        try:
            found = fn()
            jobs.extend(found)
            stats.append({"source": label, "count": len(found), "error": None})
        except FetchError as exc:
            stats.append({"source": label, "count": 0, "error": str(exc)})
        except Exception as exc:  # never let one bad source abort the scan
            stats.append({"source": label, "count": 0, "error": f"unexpected: {exc}"})

    for entry in sources_cfg.get("greenhouse", []) or []:
        token = entry.get("token")
        if token:
            _run(f"greenhouse/{token}", lambda t=token, e=entry: greenhouse.fetch(t, e.get("company")))

    for entry in sources_cfg.get("lever", []) or []:
        site = entry.get("site")
        if site:
            _run(f"lever/{site}", lambda s=site, e=entry: lever.fetch(s, e.get("company")))

    for entry in sources_cfg.get("ashby", []) or []:
        org = entry.get("org")
        if org:
            _run(f"ashby/{org}", lambda o=org, e=entry: ashby.fetch(o, e.get("company")))

    rcfg = sources_cfg.get("remotive") or {}
    if rcfg.get("enabled"):
        limit = int(rcfg.get("limit_per_keyword", 50))
        for kw in profile.remotive_queries(int(rcfg.get("max_keywords", 6))):
            _run(f"remotive/{kw}", lambda k=kw: remotive.fetch(k, limit))

    lcfg = sources_cfg.get("linkedin") or {}
    if lcfg.get("enabled"):
        locations = lcfg.get("locations") or ["United States"]
        kws = profile.search_keywords[: int(lcfg.get("max_keywords", 4))]
        pairs = [(kw, loc) for kw in kws for loc in locations]
        random.shuffle(pairs)  # vary request order each run (no fixed pattern)
        min_d = float(lcfg.get("min_delay_seconds", 3.0))
        max_d = float(lcfg.get("max_delay_seconds", 7.0))
        pages = int(lcfg.get("pages_per_query", 1))
        budget = int(lcfg.get("max_requests", 20))  # hard safety cap per run
        used = 0
        for i, (kw, loc) in enumerate(pairs):
            if used >= budget:
                stats.append({"source": "linkedin", "count": 0,
                              "error": f"request budget ({budget}) reached — stopping; apply by hand"})
                break
            if i > 0:
                time.sleep(random.uniform(min_d, max_d))  # jittered pause between queries
            _run(
                f"linkedin/{kw}@{loc}",
                lambda k=kw, l=loc: linkedin.fetch(
                    k, l,
                    experience=str(lcfg.get("experience_levels", "2,3")),
                    posted_within_days=int(lcfg.get("posted_within_days", 7)),
                    pages=pages, min_delay=min_d, max_delay=max_d,
                ),
            )
            used += pages

    return _dedupe(jobs), stats
