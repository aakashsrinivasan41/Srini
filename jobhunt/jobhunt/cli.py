"""jobhunt command-line interface.

  python -m jobhunt.cli fetch                 # ATS boards only -> data/jobs.json
  python -m jobhunt.cli apify [--only LABEL] [--limit N]   # run Apify searches
  python -m jobhunt.cli all                   # ATS + Apify combined
  python -m jobhunt.cli rank [--top N] [--all]            # score + shortlist
  python -m jobhunt.cli discover "Company"    # find a company's ATS + slug
  python -m jobhunt.cli letter <job_index>    # draft a cover letter for a ranked job
  python -m jobhunt.cli apply <job_index> [--submit]      # browser autofill
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

from . import aggregate
from .models import DATA_DIR, load_profile, business_age_days, is_us
from .score import rank as rank_jobs, shortlist as shortlist_jobs


def _age_label(posted_at: str) -> str:
    """Business-day age, e.g. '0D', '1D', '?' if unknown."""
    d = business_age_days(posted_at)
    return "?" if d is None else f"{d}D"


def _load_env() -> None:
    """Lightweight .env loader so ANTHROPIC_API_KEY / APIFY_TOKEN just work."""
    import os
    env = Path(__file__).resolve().parent.parent / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def cmd_fetch(_args) -> None:
    jobs = aggregate.fetch_all()
    aggregate.save(jobs)
    print(f"\nSaved {len(jobs)} jobs -> {DATA_DIR/'jobs.json'}")


def cmd_apify(args) -> None:
    jobs = aggregate.fetch_apify(only=args.only)
    if args.limit:
        jobs = jobs[: args.limit]
    # merge into existing jobs.json so rank sees everything
    existing = aggregate.load() if (DATA_DIR / "jobs.json").exists() else []
    merged = aggregate._dedupe(existing + jobs)
    aggregate.save(merged)
    print(f"\nSaved {len(jobs)} apify jobs (merged total {len(merged)}) -> {DATA_DIR/'jobs.json'}")


def cmd_linkedin(args) -> None:
    jobs = aggregate.fetch_linkedin(only=args.only)
    if args.limit:
        jobs = jobs[: args.limit]
    existing = aggregate.load() if (DATA_DIR / "jobs.json").exists() else []
    merged = aggregate._dedupe(existing + jobs)
    aggregate.save(merged)
    print(f"\nSaved {len(jobs)} linkedin jobs (merged total {len(merged)}) -> {DATA_DIR/'jobs.json'}")


def cmd_all(_args) -> None:
    jobs = aggregate.fetch_combined(use_apify=True, use_linkedin=True)
    aggregate.save(jobs)
    print(f"\nSaved {len(jobs)} jobs -> {DATA_DIR/'jobs.json'}")


def cmd_rank(args) -> None:
    p = load_profile()
    jobs = aggregate.load()

    # US-only by default (drop London/Singapore/EMEA/etc.); --global to keep all
    if not args.glob:
        before = len(jobs)
        jobs = [j for j in jobs if is_us(j.location)]
        if before != len(jobs):
            print(f"(US-only: kept {len(jobs)} of {before}; pass --global to include non-US)")

    ranked = rank_jobs(jobs, p) if args.all else shortlist_jobs(jobs, p)

    # staleness filter in BUSINESS days. Unknown-date postings are always kept.
    def _within(jobs, n):
        return [j for j in jobs
                if (business_age_days(j.posted_at) is None) or (business_age_days(j.posted_at) <= n)]

    if args.all_ages:
        pass                                   # show every age
    elif args.max_age is not None:             # explicit -> strict, no widening
        before = len(ranked)
        ranked = _within(ranked, args.max_age)
        print(f"(age filter: kept {len(ranked)} of {before} within {args.max_age} "
              f"business day(s); unknown-date kept; --all-ages to disable)")
    else:                                       # default 3, auto-widen if empty
        before = len(ranked)
        for w in (3, 5, 10, 20):
            filtered = _within(ranked, w)
            if filtered:
                ranked = filtered
                extra = "" if w == 3 else f" (auto-widened from 3 — nothing fresher available)"
                print(f"(age filter: kept {len(ranked)} of {before} within {w} business "
                      f"day(s){extra}; --max-age N to set your own, --all-ages to disable)")
                break
        else:
            print(f"(age filter: no postings within 20 business days; showing all {before})")

    if args.top:
        ranked = ranked[: args.top]

    # console table
    print(f"\n{'#':>3}  {'score':>5}  {'age':>5}  {'company':<16} {'title':<40} {'location':<20}")
    print("-" * 100)
    for i, j in enumerate(ranked):
        print(f"{i:>3}  {j.score:>5}  {_age_label(j.posted_at):>5}  "
              f"{j.company[:16]:<16} {j.title[:40]:<40} {j.location[:20]:<20}")

    # csv export
    out = DATA_DIR / "ranked.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["index", "score", "age", "posted_at", "company", "title", "location",
                    "remote", "comp_min", "comp_max", "url", "source", "why"])
        for i, j in enumerate(ranked):
            why = " | ".join(f"{k}:{v}" for k, v in j.score_breakdown.items())
            w.writerow([i, j.score, _age_label(j.posted_at), j.posted_at, j.company, j.title,
                        j.location, j.remote, j.comp_min, j.comp_max, j.url, j.source, why])
    # persist ranked order so `letter`/`apply`/`open` can resolve an index
    aggregate.save(ranked, DATA_DIR / "ranked.json")

    # clickable HTML page
    from .report import write_html
    html_path = write_html(ranked)
    print(f"\n{len(ranked)} jobs -> {out}")
    print(f"Clickable list -> {html_path}")
    if args.open:
        import webbrowser
        webbrowser.open(f"file://{html_path.resolve()}")
        print("Opened in your browser.")
    else:
        print("Tip: add --open to pop the clickable list in your browser,")
        print("     or `python -m jobhunt.cli open <#>` to jump straight to one job.")


def cmd_discover(args) -> None:
    from .discover import main as discover_main
    discover_main(args.company)


def _ranked_job(index: int):
    path = DATA_DIR / "ranked.json"
    if not path.exists():
        sys.exit("Run `rank` first so jobs have a stable index.")
    jobs = aggregate.load(path)
    if not 0 <= index < len(jobs):
        sys.exit(f"Index {index} out of range (0..{len(jobs)-1}).")
    return jobs[index]


def cmd_open(args) -> None:
    import webbrowser
    job = _ranked_job(args.index)
    if not job.url:
        sys.exit(f"#{args.index} ({job.title}) has no URL on record.")
    print(f"Opening #{args.index}: {job.title} @ {job.company}\n  {job.url}")
    webbrowser.open(job.url)


def cmd_letter(args) -> None:
    from .generate import cover_letter
    job = _ranked_job(args.index)
    print(f"\n# Cover letter — {job.title} @ {job.company}\n")
    print(cover_letter(job))


def cmd_apply(args) -> None:
    from .autofill import autofill
    job = _ranked_job(args.index)
    answers = {}
    if args.cover:
        from .generate import cover_letter
        answers["cover"] = cover_letter(job)
    print(f"Opening application for {job.title} @ {job.company}")
    autofill(job.url, submit=args.submit, answers=answers)


def main(argv=None) -> None:
    _load_env()
    ap = argparse.ArgumentParser(prog="jobhunt", description="Aggregate, rank, and assist job applications.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("fetch", help="fetch ATS boards -> jobs.json").set_defaults(func=cmd_fetch)

    a = sub.add_parser("apify", help="run Apify searches (LinkedIn/Indeed)")
    a.add_argument("--only", help="run only the search with this label")
    a.add_argument("--limit", type=int, help="cap number of jobs kept")
    a.set_defaults(func=cmd_apify)

    li = sub.add_parser("linkedin", help="run LinkedIn guest-endpoint searches (free)")
    li.add_argument("--only", help="run only the search with this label")
    li.add_argument("--limit", type=int, help="cap number of jobs kept")
    li.set_defaults(func=cmd_linkedin)

    sub.add_parser("all", help="ATS + Apify + LinkedIn combined").set_defaults(func=cmd_all)

    r = sub.add_parser("rank", help="score jobs and print shortlist")
    r.add_argument("--top", type=int, help="show only top N")
    r.add_argument("--all", action="store_true", help="show all (not just shortlist)")
    r.add_argument("--open", action="store_true", help="open the clickable HTML list in your browser")
    r.add_argument("--max-age", type=int, metavar="BDAYS",
                   help="hide postings older than N business days (default 3; weekends roll forward)")
    r.add_argument("--all-ages", action="store_true", help="disable the staleness filter, show every age")
    r.add_argument("--global", dest="glob", action="store_true",
                   help="include non-US postings (default is US-only)")
    r.set_defaults(func=cmd_rank)

    o = sub.add_parser("open", help="open a ranked job's application page in your browser")
    o.add_argument("index", type=int)
    o.set_defaults(func=cmd_open)

    d = sub.add_parser("discover", help="find a company's ATS + slug")
    d.add_argument("company")
    d.set_defaults(func=cmd_discover)

    l = sub.add_parser("letter", help="draft a cover letter for a ranked job index")
    l.add_argument("index", type=int)
    l.set_defaults(func=cmd_letter)

    ap_ = sub.add_parser("apply", help="open browser autofill for a ranked job index")
    ap_.add_argument("index", type=int)
    ap_.add_argument("--submit", action="store_true", help="allow auto-submit after y/N prompt")
    ap_.add_argument("--cover", action="store_true", help="also draft+prefill a cover letter")
    ap_.set_defaults(func=cmd_apply)

    args = ap.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
