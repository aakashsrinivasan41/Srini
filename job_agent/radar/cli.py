"""Command-line interface:  python3 -m radar <command>

  scan      fetch all sources, score, store, write report.html
  list      show tracked open jobs (CLI table)
  report    regenerate report.html from the database
  open      open report.html in your browser
  mark      mark a job:  mark <id> applied|skipped|hidden
  sources   list configured sources
  demo      build a report from bundled samples (no network)
  selftest  run the offline logic self-test
"""
from __future__ import annotations

import argparse
import os
import sys
import webbrowser

from .matching import Matcher
from .profile import ProfileError, load_profile, load_sources
from .report import cli_table, render_html
from .runner import collect
from .state import Store

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # .../job_agent
DB_PATH = os.path.join(BASE_DIR, ".cache", "radar.sqlite")
REPORT_PATH = os.path.join(BASE_DIR, "report.html")


def _write_report(rows, stats, profile_name):
    with open(REPORT_PATH, "w", encoding="utf-8") as fh:
        fh.write(render_html(rows, stats, profile_name))
    return REPORT_PATH


def cmd_scan(args):
    try:
        profile = load_profile(BASE_DIR)
    except ProfileError as exc:
        print(f"error: {exc}")
        return 2
    if profile.is_example:
        print("note: using profile.example.yaml — copy it to profile.yaml and add your real details.\n")

    sources_cfg = load_sources(BASE_DIR)
    if not sources_cfg:
        print("error: config/sources.yaml not found or empty. Add some company boards first.")
        return 2

    print("Scanning sources...")
    jobs, stats = collect(sources_cfg, profile)
    for s in stats:
        flag = f"ERROR ({s['error']})" if s["error"] else f"{s['count']} jobs"
        print(f"  {s['source']:<28} {flag}")

    matcher = Matcher(profile)
    matched = [matcher.evaluate(j, strict_location=args.strict_location) for j in jobs]
    keep = [j for j in matched if not j.rejected and j.score >= args.min_score]
    print(f"\nFetched {len(jobs)} jobs · {len(keep)} match your profile.")
    li_n = sum(1 for j in keep if j.source == "linkedin")
    if li_n:
        warn = " — that's a lot; triage and apply by hand" if li_n > 25 else " — apply to these by hand"
        print(f"  ({li_n} from LinkedIn{warn}; automated LinkedIn applying risks your account)")

    store = Store(DB_PATH)
    res = store.upsert(keep)
    rows = store.fetch(min_score=args.min_score)
    print(f"New: {res['new']} · updated: {res['updated']} · open in tracker: {len(rows)}\n")
    print(cli_table(rows))
    path = _write_report(rows, stats, profile.name)
    store.demote_new_to_seen()
    store.close()
    print(f"\nDashboard: {path}\n(open it with:  python3 -m radar open )")
    return 0


def cmd_list(args):
    store = Store(DB_PATH)
    statuses = ("new", "seen", "applied", "skipped", "hidden") if args.all else ("new", "seen")
    rows = store.fetch(statuses=statuses, min_score=args.min_score, source=args.source)
    store.close()
    print(cli_table(rows, limit=args.limit))
    return 0


def cmd_report(args):
    try:
        profile = load_profile(BASE_DIR)
        name = profile.name
    except ProfileError:
        name = "(unknown)"
    store = Store(DB_PATH)
    rows = store.fetch()
    store.close()
    path = _write_report(rows, [{"source": "regenerated from database", "count": len(rows), "error": None}], name)
    print(f"Wrote {path} ({len(rows)} jobs).")
    return 0


def cmd_open(args):
    if not os.path.exists(REPORT_PATH):
        print("No report yet — run `scan` or `demo` first.")
        return 1
    webbrowser.open("file://" + REPORT_PATH)
    print(f"Opening {REPORT_PATH}")
    return 0


def cmd_mark(args):
    store = Store(DB_PATH)
    ok = store.set_status(args.id, args.status)
    store.close()
    print(f"{'Marked' if ok else 'No job found for id'}: {args.id} -> {args.status}")
    return 0 if ok else 1


def cmd_sources(args):
    cfg = load_sources(BASE_DIR)
    if not cfg:
        print("No config/sources.yaml found.")
        return 1
    for kind in ("greenhouse", "lever", "ashby"):
        for e in cfg.get(kind, []) or []:
            ident = e.get("token") or e.get("site") or e.get("org")
            print(f"  {kind:<11} {ident:<22} {e.get('company', '')}")
    r = cfg.get("remotive") or {}
    print(f"  remotive    enabled={bool(r.get('enabled'))}")
    return 0


def cmd_demo(args):
    from . import fixtures
    try:
        profile = load_profile(BASE_DIR)
    except ProfileError as exc:
        print(f"error: {exc}")
        return 2
    matcher = Matcher(profile)
    keep = [j for j in (matcher.evaluate(j) for j in fixtures.demo_jobs()) if not j.rejected]
    store = Store(os.path.join(BASE_DIR, ".cache", "demo.sqlite"))
    store.conn.execute("DELETE FROM jobs")
    store.conn.commit()
    store.upsert(keep)
    rows = store.fetch()
    store.close()
    print(cli_table(rows))
    with open(REPORT_PATH, "w", encoding="utf-8") as fh:
        fh.write(render_html(rows, [{"source": "demo (sample data)", "count": len(rows), "error": None}], profile.name))
    print(f"\nDemo dashboard written to {REPORT_PATH}")
    return 0


def cmd_selftest(args):
    from . import selftest
    return selftest.run(BASE_DIR)


def build_parser():
    p = argparse.ArgumentParser(prog="radar", description="Profile-driven job search radar.")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("scan", help="fetch, score, store, build report")
    s.add_argument("--min-score", type=float, default=0.0)
    s.add_argument("--strict-location", action="store_true", help="drop roles outside NY/SF/remote")
    s.set_defaults(func=cmd_scan)

    s = sub.add_parser("list", help="show tracked jobs")
    s.add_argument("--all", action="store_true")
    s.add_argument("--min-score", type=float, default=0.0)
    s.add_argument("--source", default=None)
    s.add_argument("--limit", type=int, default=40)
    s.set_defaults(func=cmd_list)

    sub.add_parser("report", help="regenerate report.html").set_defaults(func=cmd_report)
    sub.add_parser("open", help="open report.html").set_defaults(func=cmd_open)

    s = sub.add_parser("mark", help="mark a job applied/skipped/hidden")
    s.add_argument("id")
    s.add_argument("status", choices=["applied", "skipped", "hidden", "new", "seen"])
    s.set_defaults(func=cmd_mark)

    sub.add_parser("sources", help="list configured sources").set_defaults(func=cmd_sources)
    sub.add_parser("demo", help="offline demo from sample data").set_defaults(func=cmd_demo)
    sub.add_parser("selftest", help="run logic self-test").set_defaults(func=cmd_selftest)
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
