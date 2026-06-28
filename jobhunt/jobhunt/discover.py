"""Find which ATS + slug a company actually uses.

Probes Greenhouse, Lever, and Ashby with candidate slugs derived from the
company name and reports any that return live postings. Run this whenever a
company in companies.yaml errors out — boards migrate between ATSes.
"""
from __future__ import annotations

import re

from .sources import FETCHERS


def _candidate_slugs(name: str) -> list[str]:
    base = name.strip().lower()
    compact = re.sub(r"[^a-z0-9]", "", base)
    dashed = re.sub(r"[^a-z0-9]+", "-", base).strip("-")
    no_suffix = re.sub(r"\b(inc|llc|corp|corporation|technologies|labs|ai)\b", "", base).strip()
    compact_ns = re.sub(r"[^a-z0-9]", "", no_suffix)
    # de-dupe, keep order
    seen, out = set(), []
    for s in (compact, dashed, compact_ns, no_suffix.replace(" ", "")):
        if s and s not in seen:
            seen.add(s)
            out.append(s)
    return out


def discover(name: str) -> list[dict]:
    hits: list[dict] = []
    for ats, fetcher in FETCHERS.items():
        for slug in _candidate_slugs(name):
            try:
                jobs = fetcher(name, slug)
            except Exception:  # noqa: BLE001
                continue
            if jobs:
                hits.append({"ats": ats, "slug": slug, "count": len(jobs)})
                break  # first working slug per ATS is enough
    return hits


def main(name: str) -> None:
    print(f"Probing ATSes for '{name}' ...")
    hits = discover(name)
    if not hits:
        print("  No public board found. Likely Workday/Taleo/iCIMS — track manually.")
        return
    for h in hits:
        print(f"  ✓ {h['ats']:10s} slug='{h['slug']}'  ({h['count']} postings)")
    best = hits[0]
    print(f"\nAdd to companies.yaml:\n"
          f"  - {{ name: {name}, ats: {best['ats']}, slug: {best['slug']}, verified: true }}")
