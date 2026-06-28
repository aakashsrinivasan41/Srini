"""Pull every configured company across all ATSes, normalize, and dedupe."""
from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

from .models import Job, DATA_DIR, CONFIG_DIR, load_companies, load_yaml
from .sources import FETCHERS


def fetch_all(verbose: bool = True) -> list[Job]:
    cfg = load_companies()
    targets = cfg.get("companies", [])
    jobs: list[Job] = []
    errors: list[str] = []

    def _one(entry: dict) -> tuple[str, list[Job] | str]:
        ats, slug, name = entry.get("ats"), entry.get("slug"), entry.get("name")
        fetcher = FETCHERS.get(ats)
        if not fetcher:
            return name, f"unknown ATS '{ats}'"
        try:
            return name, fetcher(name, slug)
        except requests.HTTPError as e:
            code = getattr(getattr(e, "response", None), "status_code", "?")
            return name, f"HTTP {code} (check slug '{slug}' on {ats}; run: discover \"{name}\")"
        except Exception as e:  # noqa: BLE001
            return name, f"{type(e).__name__}: {e}"

    with ThreadPoolExecutor(max_workers=8) as ex:
        futures = [ex.submit(_one, e) for e in targets]
        for fut in as_completed(futures):
            name, result = fut.result()
            if isinstance(result, str):
                errors.append(f"  ✗ {name}: {result}")
            else:
                jobs.extend(result)
                if verbose:
                    print(f"  ✓ {name}: {len(result)} postings")

    if verbose and errors:
        print("\nSources with issues:")
        print("\n".join(errors))

    deduped = _dedupe(jobs)
    if verbose:
        print(f"\nTotal: {len(jobs)} fetched, {len(deduped)} after dedupe")
    return deduped


def fetch_apify(only: str | None = None, verbose: bool = True) -> list[Job]:
    """Run the searches in config/apify.yaml (LinkedIn/Indeed/etc via Apify)."""
    from .sources.apify import fetch_search  # local import: optional dependency path

    cfg_path = CONFIG_DIR / "apify.yaml"
    if not cfg_path.exists():
        return []
    searches = (load_yaml(cfg_path) or {}).get("searches", [])
    jobs: list[Job] = []
    for s in searches:
        label = s.get("label", s.get("actor", "?"))
        if only and only != label:
            continue
        try:
            got = fetch_search(s)
            jobs.extend(got)
            if verbose:
                print(f"  ✓ apify:{label}: {len(got)} postings")
        except Exception as e:  # noqa: BLE001
            if verbose:
                print(f"  ✗ apify:{label}: {type(e).__name__}: {e}")
    return jobs


def fetch_combined(use_apify: bool = True, verbose: bool = True) -> list[Job]:
    """ATS boards + (optionally) Apify aggregators, deduped together."""
    jobs = fetch_all(verbose=verbose)  # already deduped within ATS set
    if use_apify:
        jobs = _dedupe(jobs + fetch_apify(verbose=verbose))
        if verbose:
            print(f"\nCombined total after Apify + dedupe: {len(jobs)}")
    return jobs


def _dedupe(jobs: list[Job]) -> list[Job]:
    seen: dict[str, Job] = {}
    for j in jobs:
        fp = j.fingerprint
        # prefer the entry that actually carries a description
        if fp not in seen or (not seen[fp].description and j.description):
            seen[fp] = j
    return list(seen.values())


def save(jobs: list[Job], path: Path | None = None) -> Path:
    path = path or (DATA_DIR / "jobs.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump([j.to_dict() for j in jobs], f, indent=2)
    return path


def load(path: Path | None = None) -> list[Job]:
    path = path or (DATA_DIR / "jobs.json")
    with open(path, "r", encoding="utf-8") as f:
        return [Job.from_dict(d) for d in json.load(f)]
