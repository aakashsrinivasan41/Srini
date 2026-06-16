# Job Application Agent

A personal, malleable job-search assistant. Everything keys off one profile
file, so it works for any person/field — swap the profile, keep the engine.

## Two tracks

| Track | What it does | Status |
|-------|--------------|--------|
| **Job Radar** (Python) | The "brain" — scans friendly boards (Greenhouse/Lever/Ashby + Remotive) during the day, scores against your profile, de-dupes, tracks status, and builds a ranked HTML dashboard. | **Ready** |
| **Claude-for-Chrome** | The "hands" — clicks into a posting and fills the fields while you supervise. Best for ugly forms (Workday) and hostile sites (LinkedIn) where you submit by hand. | **Ready** |

Both tracks read the **same profile**, which is what makes the whole thing
portable to someone in a different field.

## Setup (one time)

```bash
cd job_agent
python3 -m pip install -r requirements.txt   # only dependency: PyYAML
cp profile.example.yaml profile.yaml         # then fill in your real details
```

`profile.yaml`, your resumes, the database, and `report.html` are all
**gitignored** — personal data never gets committed.

## Job Radar — usage

```bash
cd job_agent

python3 -m radar selftest     # prove the logic works (no network)
python3 -m radar demo         # build a dashboard from sample data (no network)

python3 -m radar scan         # the real thing: fetch, score, store, build report
python3 -m radar open         # open report.html in your browser
python3 -m radar list         # ranked table in the terminal
python3 -m radar list --all   # include applied/skipped/hidden
python3 -m radar mark <id> applied   # also: skipped | hidden
python3 -m radar sources      # show configured boards
```

`scan` prints, per board, how many jobs it returned (or an error), so a wrong
token is obvious immediately. Add `--strict-location` to drop anything outside
NY metro / SF Bay / remote; `--min-score N` to raise the bar.

### Picking which companies to scan

Edit `config/sources.yaml`. Find a company's identifier from its careers URL:

| ATS | URL pattern | use |
|-----|-------------|-----|
| Greenhouse | `boards.greenhouse.io/<token>` | `<token>` |
| Lever | `jobs.lever.co/<site>` | `<site>` |
| Ashby | `jobs.ashbyhq.com/<org>` | `<org>` |

The seeded list is just a starting point — replace it with your targets
(FactSet-adjacent data/fintech shops, asset managers, etc.).

### What gets scored (every profile signal is used)

- `target_roles.core` / `target_roles.adjacent` — weighted positive matches
- `search_keywords` — additional positive matches
- `exclude_keywords` — drop sales/CS/AM + seniority titles (the `manager`
  rule is smart enough to keep "Associate Product Manager")
- `locations` — NY metro > SF Bay > remote ranking; `--strict-location` filters
- `rules.salary.hard_floor_usd` — drop roles whose posted max is below the floor
- `rules.salary.anchor_usd` — compute a "suggested ask" per posting
- `rules.experience_cap_years` — drop roles that clearly require more years

## Run it automatically during the day (macOS `launchd`)

Save as `~/Library/LaunchAgents/com.jobradar.scan.plist` (edit the path), then
`launchctl load ~/Library/LaunchAgents/com.jobradar.scan.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.jobradar.scan</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/zsh</string><string>-c</string>
    <string>cd /Users/YOU/path/to/job_agent && /usr/bin/python3 -m radar scan</string>
  </array>
  <key>StartCalendarInterval</key>
  <array>
    <dict><key>Hour</key><integer>10</integer><key>Minute</key><integer>0</integer></dict>
    <dict><key>Hour</key><integer>14</integer><key>Minute</key><integer>0</integer></dict>
  </array>
  <key>StandardOutPath</key><string>/tmp/jobradar.log</string>
  <key>StandardErrorPath</key><string>/tmp/jobradar.err</string>
</dict></plist>
```

(Or a cron line: `0 10,14 * * 1-5 cd /path/to/job_agent && /usr/bin/python3 -m radar scan`.)
You come home, run `python3 -m radar open`, review the new finds, and hand the
good ones to Claude-for-Chrome to fill in.

## Using Claude-for-Chrome (the "hands")

1. Copy the standing instructions from `claude_chrome_prompt.md`.
2. Keep your info sheet (your real personal details) open in a tab.
3. Open a posting → Claude side panel → paste → it fills the form, stops before
   submit, and pauses on logins/CAPTCHAs.

## Architecture

```
job_agent/
  profile.example.yaml      # template (committed); copy -> profile.yaml (gitignored)
  claude_chrome_prompt.md   # standing instructions for Claude-for-Chrome
  requirements.txt
  config/sources.yaml       # which company boards to scan
  radar/
    cli.py                  # `python3 -m radar <command>`
    runner.py               # fetch all sources, isolate per-source failures
    matching.py             # scoring + filtering (all profile signals)
    state.py                # SQLite: de-dup + status tracking
    report.py               # CLI table + self-contained HTML dashboard
    profile.py              # load/normalize profile.yaml
    sources/                # greenhouse, lever, ashby, remotive adapters
    fixtures.py + selftest.py  # offline tests / demo data
```

## Portability (give it to a friend)

Hand them this folder. They run setup, then edit two files: `profile.yaml`
(their identity + `target_roles` + `search_keywords` + `exclude_keywords`) and
`config/sources.yaml` (companies in their field — e.g. pharma/biotech boards).
The engine, scoring, salary logic, and dashboard all stay the same.

## Privacy

Real personal data (`profile.yaml`, resumes, the database, `report.html`) is
gitignored and never committed. Only the template, code, and instructions live
in git.
