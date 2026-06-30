"""Enrichment: fetch the FULL posting for top candidates so the comp/experience
filters can see what the list card hid.

LinkedIn (and Indeed list cards) often omit salary and the years-required text.
That lets a role with a perfect title but a $65k salary or a "6+ years" demand
rank high on title alone. This module pulls each candidate's detail page, fills
in description + salary, so re-scoring applies the real comp/experience gates.

LinkedIn guest detail endpoint (no login):
  https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}
Returns an HTML fragment with the full description and (often) a salary line.

Runs on the user's machine. Paced + backs off on 429; skips failures quietly.
"""
from __future__ import annotations

import re
import time

import requests

from .models import strip_html, parse_comp, Job

DETAIL = "https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{id}"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

_DESC = re.compile(r'show-more-less-html__markup[^>]*>(.*?)</div>', re.S)
_DESC2 = re.compile(r'description__text[^>]*>(.*?)</section>', re.S)
_SALARY = re.compile(r'compensation__salary[^>]*>(.*?)<', re.S)
_ID = re.compile(r'-(\d{6,})(?:\?|/|$)')


def _job_id(job: Job) -> str | None:
    if job.job_id and job.job_id.isdigit():
        return job.job_id
    m = _ID.search(job.url or "")
    return m.group(1) if m else None


def enrich_linkedin(job: Job) -> bool:
    """Fetch the full posting and fill job.description + comp. True if updated.

    Raises requests.HTTPError on 429 so the caller can stop the batch early.
    """
    jid = _job_id(job)
    if not jid:
        return False
    r = requests.get(DETAIL.format(id=jid), headers={"User-Agent": UA, "Accept": "text/html"}, timeout=25)
    if r.status_code == 429:
        raise requests.HTTPError("429 rate-limited by LinkedIn")
    if r.status_code != 200:
        return False
    html = r.text
    m = _DESC.search(html) or _DESC2.search(html)
    if m:
        job.description = strip_html(m.group(1))
    # salary: prefer the explicit comp line, else scan the description text
    cmin = cmax = None
    sm = _SALARY.search(html)
    if sm:
        cmin, cmax = parse_comp(sm.group(1))
    if not cmin and job.description:
        cmin, cmax = parse_comp(job.description)
    if cmin:
        job.comp_min, job.comp_max = cmin, cmax
    return bool(m or cmin)


def enrich_jobs(jobs: list[Job], limit: int = 40, pace: float = 1.0,
                verbose: bool = True) -> list[Job]:
    """Enrich up to `limit` LinkedIn jobs (in the order given) that are missing
    salary or description. Mutates the Job objects in place."""
    targets = [j for j in jobs
               if j.source.startswith("linkedin") and (not j.comp_min or not j.description)][:limit]
    if verbose:
        print(f"Enriching {len(targets)} top LinkedIn postings (fetching full salary/description)...")
    done = 0
    for j in targets:
        try:
            if enrich_linkedin(j):
                done += 1
        except requests.HTTPError:
            if verbose:
                print("  (LinkedIn throttled — stopping enrichment early; re-run later for the rest)")
            break
        except Exception:  # noqa: BLE001
            pass
        time.sleep(pace)
    if verbose:
        print(f"  enriched {done}/{len(targets)} with real salary + description")
    return jobs
