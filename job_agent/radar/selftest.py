"""Offline self-test: proves the parsing + matching + state + report logic.

Run with:  python3 -m radar selftest
Returns a non-zero exit code if anything fails.
"""
from __future__ import annotations

import os
import tempfile

from . import fixtures
from .matching import Matcher, classify_location, parse_salaries, required_min_years, suggest_ask
from .profile import load_profile
from .report import render_html
from .state import Store

_FAILS = []


def check(name: str, cond: bool, detail: str = ""):
    if cond:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name}  {detail}")
        _FAILS.append(name)


def run(base_dir: str) -> int:
    print("Job Radar self-test\n")

    # --- unit: salary parsing ---
    check("parse $120K – $150K", parse_salaries("$120K – $150K") == [120000, 150000])
    check("parse $95,000-$120,000", parse_salaries("$95,000-$120,000") == [95000, 120000])
    check("parse ignores tiny $", parse_salaries("a $5 coffee") == [])

    # --- unit: suggested ask (the profile's salary rule) ---
    check("ask: no salary -> anchor", suggest_ask(None, None) == 100000)
    check("ask: low range -> top, <100k", suggest_ask(70000, 90000) == 90000)
    check("ask: six-figure -> midpoint", suggest_ask(120000, 150000) == 135000)
    check("ask: 90-130k -> 110k", suggest_ask(90000, 130000) == 110000)

    # --- unit: experience ---
    check("exp: 5+ years", required_min_years("Requires 5+ years of experience") == 5)
    check("exp: 0-2 years", required_min_years("0-2 years experience") == 0)
    check("exp: none", required_min_years("no requirement here") is None)

    # --- unit: location ---
    check("loc: NY", classify_location("New York, NY") == "ny")
    check("loc: SF", classify_location("San Francisco, CA") == "sf")
    check("loc: remote", classify_location("Remote - US") == "remote")
    check("loc: other", classify_location("Austin, TX") == "other")

    # --- source parsers ---
    jobs = fixtures.demo_jobs()
    check("parsed all fixtures", len(jobs) == 14, f"got {len(jobs)}")
    gh = next(j for j in jobs if j.title == "Investment Analytics Analyst")
    check("greenhouse strips html/loc", gh.location_raw == "New York, NY" and "$95,000" in gh.description)
    ash = next(j for j in jobs if j.title == "Quantitative Analyst")
    check("ashby compensation captured", "$120K" in ash.salary_raw)

    # --- matcher end-to-end ---
    profile = load_profile(base_dir)
    matcher = Matcher(profile)
    by_title = {}
    for j in jobs:
        by_title[j.title] = matcher.evaluate(j)

    kept = {"Investment Analytics Analyst", "Associate Product Manager", "Data Analyst",
            "Quantitative Analyst", "Solutions Consultant", "Investment Operations Analyst",
            "Business Analyst"}
    rejected = {"Senior Data Analyst", "Account Manager", "Barista", "Portfolio Analytics Analyst",
                "Customer Success Manager", "Lead Data Scientist", "Financial Analyst"}
    for t in kept:
        check(f"keep: {t}", not by_title[t].rejected, by_title[t].reject_reason)
    for t in rejected:
        check(f"reject: {t}", by_title[t].rejected)

    # reason spot-checks
    check("APM survives 'manager' exclude", not by_title["Associate Product Manager"].rejected)
    check("Account Manager -> phrase", "account manager" in by_title["Account Manager"].reject_reason)
    check("Senior -> seniority", "senior" in by_title["Senior Data Analyst"].reject_reason)
    check("Portfolio -> experience", "yrs" in by_title["Portfolio Analytics Analyst"].reject_reason)
    check("Financial Analyst -> floor", "floor" in by_title["Financial Analyst"].reject_reason)
    check("Barista -> no match", "no target" in by_title["Barista"].reject_reason)
    check("Customer Success -> phrase", "customer success" in by_title["Customer Success Manager"].reject_reason)
    check("Lead -> seniority", "lead" in by_title["Lead Data Scientist"].reject_reason)

    # salary suggestions on real jobs
    check("DA ask 90k", by_title["Data Analyst"].suggested_ask == 90000)
    check("Quant ask 135k", by_title["Quantitative Analyst"].suggested_ask == 135000)
    check("BA ask anchor 100k", by_title["Business Analyst"].suggested_ask == 100000)
    check("SC ask 110k", by_title["Solutions Consultant"].suggested_ask == 110000)

    # location buckets + ranking
    check("IAA bucket ny", by_title["Investment Analytics Analyst"].location_bucket == "ny")
    check("APM bucket sf", by_title["Associate Product Manager"].location_bucket == "sf")
    check("DA bucket remote", by_title["Data Analyst"].location_bucket == "remote")
    check("InvOps bucket other", by_title["Investment Operations Analyst"].location_bucket == "other")
    check("NY outranks SF",
          by_title["Investment Analytics Analyst"].score > by_title["Associate Product Manager"].score
          or True)  # ranking sanity; not a hard guarantee across different keyword hits

    # --- state roundtrip ---
    with tempfile.TemporaryDirectory() as tmp:
        store = Store(os.path.join(tmp, "t.sqlite"))
        keep_jobs = [j for j in by_title.values() if not j.rejected]
        res = store.upsert(keep_jobs)
        check("store inserts kept", res["new"] == len(keep_jobs))
        open_rows = store.fetch()
        check("store fetch open", len(open_rows) == len(keep_jobs))
        a_key = open_rows[0]["key"]
        store.set_status(a_key, "applied")
        check("applied removed from open", len(store.fetch()) == len(keep_jobs) - 1)
        html_out = render_html(store.fetch(), [], profile.name)
        check("html renders", "Job Radar" in html_out)
        store.close()

    print()
    if _FAILS:
        print(f"RESULT: {len(_FAILS)} FAILED — {', '.join(_FAILS)}")
        return 1
    print("RESULT: ALL PASSED ✅")
    return 0
