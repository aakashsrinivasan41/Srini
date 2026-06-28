# jobhunt

A personal job-search automation toolkit: **aggregate → rank → draft → assist-apply**,
tuned to one candidate's profile. Built for Aakash Srinivasan's search (early-career
solutions / analytics / strategy-ops roles), but every preference lives in
`config/profile.yaml`, so it re-targets by editing one file.

It automates the *tedium* — finding postings, scoring them against your exact
criteria, drafting tailored materials, pre-filling the form — and keeps a human
checkpoint on the one irreversible step (hitting submit).

```
 sources/ ─┐
 (ATS +    ├─►  aggregate ─►  score ─►  shortlist ─►  generate ─►  autofill
  Apify)  ─┘   (dedupe)     (0-100)   (CSV/JSON)    (Claude)     (Playwright)
```

## What it does, honestly

| Stage | Status | Notes |
|---|---|---|
| Search & aggregate | ✅ Full | Greenhouse/Lever/Ashby **public JSON APIs** (no scraping) + LinkedIn/Indeed/Glassdoor via **Apify**. |
| Filter & rank | ✅ Full | Weighted score against location / comp / role / arrangement / company, plus an **experience guardrail**. |
| Draft cover letters & answers | ✅ Full | Claude API, grounded in your resume, with a hallucination guard. |
| Fill the application | ⚠️ Assisted | Pre-fills fields + uploads resume, then **stops for you to review & submit**. |
| Blind auto-submit | 🚫 Default off | See "Responsible use" below. Opt-in flag exists; keep it off. |

## Setup

```bash
cd jobhunt
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium          # only needed for `apply`
cp .env.example .env                 # add ANTHROPIC_API_KEY and/or APIFY_TOKEN
mkdir -p assets && cp /path/to/Aakash_Srinivasan_Resume.pdf assets/
```

Then point `resume_path` in `config/profile.yaml` at that file.

## The 60-second workflow

```bash
# 1. Confirm your target companies' ATS slugs are right (boards migrate)
python -m jobhunt.cli discover "Anthropic"
python -m jobhunt.cli discover "Ramp"

# 2. Pull everything (free ATS boards + Apify aggregators)
python -m jobhunt.cli all          # or `fetch` for ATS only / `apify` for aggregators only

# 3. Rank against your profile -> prints a table, writes data/ranked.csv
python -m jobhunt.cli rank --top 25

# 4. Draft a cover letter for shortlist row #3
python -m jobhunt.cli letter 3

# 5. Open the application, pre-filled, for you to review and submit
python -m jobhunt.cli apply 3 --cover
```

## Configuration files

- **`config/profile.yaml`** — the single source of truth. Identity, ranked
  location tiers, comp floors, role include/exclude lists, scoring weights,
  and the experience guardrail. Edit freely.
- **`config/companies.yaml`** — target companies + which ATS each uses. Slugs
  are best-effort seeds; verify with `discover`.
- **`config/apify.yaml`** — LinkedIn/Indeed/etc. searches. Each entry's `input`
  must match that actor's schema (see its Apify Store page).

## How ranking works

Each job gets a 0–100 score from five weighted components (role, location, comp,
arrangement, company) defined in `profile.yaml > weights`. Two hard rules layer on top:

1. **Excluded titles** (Portfolio Manager, Senior/Staff/Principal Engineer,
   Director+, intern…) → score 0.
2. **Experience guardrail** (`profile.yaml > experience`): the description is
   parsed for required years. Anything over `max_required_years` (default 4),
   or carrying quant/PhD/senior-eng signals, is multiplied down to near-zero —
   so 5y+/quant roles never waste a shortlist slot. Early-career phrasing gets a
   small nudge up.

`score_breakdown` (in `ranked.csv`) shows exactly why each job scored what it did.

### Tuning notes
- **On-site comp gate:** per your rule, on-site roles below `compensation.onsite_floor`
  ($125k) are knocked down hard. Postings that don't state hybrid/remote are
  *treated as on-site* — conservative. If you're getting too few results, lower
  the floor or add cities to the hybrid detection.
- **Shortlist threshold:** `profile.yaml > shortlist_threshold` (default 55).

## Responsible use

- **Aggregation** uses official public APIs (Greenhouse/Lever/Ashby) and Apify
  actors — no logging into sites and scraping behind auth.
- **Auto-submit is off by default and should stay that way.** Most ATS terms
  prohibit automated submission, and one wrong dropdown on a real application is
  unrecoverable. `autofill` fills what it safely can, deliberately leaves
  judgment fields (work auth, sponsorship, EEO) to you, and hands you the tab.
- **Never fabricate.** The cover-letter writer is constrained to facts in your
  profile and flags anything it can't trace back. Keep that guard on.
- Respect each site's rate limits and ToS. This is a personal-use accelerator,
  not a mass-application bot.

## Layout

```
config/        profile.yaml · companies.yaml · apify.yaml
jobhunt/
  models.py        Job dataclass, config loading, comp parsing
  sources/         greenhouse · lever · ashby · apify adapters
  aggregate.py     fetch all sources, dedupe, save/load
  score.py         weighted scoring + shortlist
  experience.py    years-of-experience / over-qualification guardrail
  generate.py      Claude cover letters + screening answers (hallucination guard)
  autofill.py      Playwright review-before-submit form filler
  discover.py      find a company's ATS + slug
  cli.py           command-line entrypoint
data/          jobs.json · ranked.csv · ranked.json (gitignored)
```
