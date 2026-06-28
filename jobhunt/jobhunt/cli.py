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
from .models import DATA_DIR, load_profile
from .score import rank as rank_jobs, shortlist as shortlist_jobs


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


def cmd_all(_args) -> None:
    jobs = aggregate.fetch_combined(use_apify=True)
    aggregate.save(jobs)
    print(f"\nSaved {len(jobs)} jobs -> {DATA_DIR/'jobs.json'}")


def cmd_rank(args) -> None:
    p = load_profile()
    jobs = aggregate.load()
    ranked = rank_jobs(jobs, p) if args.all else shortlist_jobs(jobs, p)
    if args.top:
        ranked = ranked[: args.top]

    # console table
    print(f"\n{'#':>3}  {'score':>5}  {'company':<16} {'title':<42} {'location':<22}")
    print("-" * 96)
    for i, j in enumerate(ranked):
        print(f"{i:>3}  {j.score:>5}  {j.company[:16]:<16} {j.title[:42]:<42} {j.location[:22]:<22}")

    # csv export
    out = DATA_DIR / "ranked.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["index", "score", "company", "title", "location", "remote",
                    "comp_min", "comp_max", "url", "source", "why"])
        for i, j in enumerate(ranked):
            why = " | ".join(f"{k}:{v}" for k, v in j.score_breakdown.items())
            w.writerow([i, j.score, j.company, j.title, j.location, j.remote,
                        j.comp_min, j.comp_max, j.url, j.source, why])
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

    sub.add_parser("all", help="ATS + Apify combined").set_defaults(func=cmd_all)

    r = sub.add_parser("rank", help="score jobs and print shortlist")
    r.add_argument("--top", type=int, help="show only top N")
    r.add_argument("--all", action="store_true", help="show all (not just shortlist)")
    r.add_argument("--open", action="store_true", help="open the clickable HTML list in your browser")
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
