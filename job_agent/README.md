# Job Application Agent

A personal, malleable job-application assistant. Everything keys off one profile
file, so it works for any person/field — swap the profile, keep the engine.

## Two tracks

| Track | What it does | Status |
|-------|--------------|--------|
| **Claude-for-Chrome** (today, no code) | The "hands" — clicks into a posting and fills the fields while you supervise. Best for ugly forms (Workday) and hostile sites (LinkedIn) where you submit by hand. | Ready now |
| **Python radar** (later) | The "brain" — scans friendly sources (Greenhouse/Lever/Ashby + aggregator APIs) during the day, ranks against your profile, dedupes, and tracks what you've applied to. | Planned |

Both tracks read the **same profile**, which is what makes the whole thing
portable to someone in a different field.

## Setup

1. Copy the template and fill in real values:
   ```bash
   cp profile.example.yaml profile.yaml
   ```
   `profile.yaml` is gitignored — your personal data stays off git.

2. Put your resume(s) in a local `resumes/` folder (also gitignored) and point
   `resume_files` in `profile.yaml` at them.

## Using Claude-for-Chrome

1. Open `claude_chrome_prompt.md` and copy the standing instructions.
2. Open your info sheet (your filled-in personal details) in a tab, or paste it
   into the Claude side panel so it has your actual values.
3. Navigate to a job posting, open the Claude side panel, paste the standing
   instructions, and let it fill the form. It stops before submit for your review
   and pauses on logins/CAPTCHAs.

## The rules (encoded in `profile.example.yaml` → `rules`)

- **Salary floor:** skip any role whose posted salary tops out under $80k.
- **Desired salary:** anchor ~$100k; ask within range if the range is low, scale
  up with the range when it reaches six figures.
- **Experience:** entry-level only; skip roles requiring more than 3 years.
- **No essays:** never write "why this company"; if an essay is *required* to
  submit, skip that application.
- **Human-in-the-loop:** never auto-submit; pause on login/CAPTCHA.

## Privacy

Real personal data (`profile.yaml`, resumes, demographic answers) is gitignored
and never committed. Only the template and instructions live in git.
