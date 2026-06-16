"""Fetch jobs from every configured source, isolating per-source failures."""
from __future__ import annotations

from typing import List, Tuple

from .httputil import FetchError
from .models import Job
from .profile import Profile
from .sources import ashby, greenhouse, lever, remotive


def _dedupe(jobs: List[Job]) -> List[Job]:
    seen, out = set(), []
    for job in jobs:
        if not job.title or not job.url:
            continue
        if job.key in seen:
            continue
        seen.add(job.key)
        out.append(job)
    return out


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

    return _dedupe(jobs), stats
