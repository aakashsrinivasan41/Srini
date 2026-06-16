"""Scoring and filtering engine.

Consumes EVERY targeting signal in the profile:
  - target_roles.core / target_roles.adjacent  (positive, weighted)
  - search_keywords                              (positive)
  - exclude_keywords                             (negative: sales/CS/AM + seniority)
  - locations (NY metro / SF Bay / remote)       (ranking + filter)
  - rules.salary.hard_floor_usd / anchor_usd     (filter + suggested ask)
  - rules.experience_cap_years                   (filter)
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import List, Optional

from .models import Job
from .profile import Profile
from .textutil import round_to

# Location alias tables (lowercase). NY/SF checked before remote so a physical
# office in those metros wins over a generic "remote" tag.
NY_ALIASES = (
    "new york", "nyc", "ny metro", "manhattan", "brooklyn", "queens",
    "jersey city", "hoboken", "newark", "stamford", "white plains",
)
SF_ALIASES = (
    "san francisco", "bay area", "palo alto", "mountain view", "menlo park",
    "sunnyvale", "san jose", "santa clara", "oakland", "redwood city",
    "foster city", "south san francisco", "san mateo", "cupertino", "berkeley",
    "emeryville", "burlingame", "daly city",
)

JUNIOR_QUALIFIERS = ("associate", "assistant", "junior", "jr", "entry", "early career", "new grad", "graduate")

# Generic connector tokens we don't reward in the per-token bonus.
_STOPWORDS = {"and", "or", "the", "of", "a", "an", "for", "to", "in", "fp&a", "&"}

_YEARS_RE = re.compile(r"(\d{1,2})\s*(?:\+|plus)?\s*(?:-|–|—|to)?\s*(\d{1,2})?\s*\+?\s*years?", re.I)
_PHD_RE = re.compile(r"ph\.?\s?d\.?[^.\n]{0,40}requir", re.I)

# Salary patterns. We only accept clearly-money tokens to avoid false positives.
_DOLLAR_K_RE = re.compile(r"(?:\$|usd)\s*(\d{2,3})\s*k\b", re.I)         # $120k / usd 120k
_PLAIN_K_RE = re.compile(r"\b(\d{2,3})\s*k\b", re.I)                     # 120k
_FULL_RE = re.compile(r"(?:\$|usd\s*)(\d{2,3}(?:,\d{3})+|\d{5,7})", re.I)  # $120,000 / usd 120000
_COMMA_RE = re.compile(r"\b(\d{2,3}(?:,\d{3})+)\b")                      # 120,000
_HOURLY_RE = re.compile(r"\$?\s*(\d{1,3}(?:\.\d+)?)\s*(?:/|per\s+)\s*(?:hr|hour)", re.I)
_RETIREMENT = {401, 403}      # 401(k)/403(b) are plans, not salaries
_HOURS_PER_YEAR = 2080


def _add(vals: set, n: float) -> None:
    if 10_000 <= n <= 1_000_000:
        vals.add(int(round(n)))


def parse_salaries(text: str) -> List[int]:
    """Extract plausible annual USD figures: $120k, $120,000, USD 120000, ranges,
    and hourly ($58/hr -> annualized). Ignores 401(k)/403(b) and tiny amounts."""
    t = text or ""
    vals: set = set()
    for m in _HOURLY_RE.finditer(t):
        _add(vals, float(m.group(1)) * _HOURS_PER_YEAR)
    for rex in (_DOLLAR_K_RE, _PLAIN_K_RE):
        for m in rex.finditer(t):
            n = int(m.group(1))
            if n not in _RETIREMENT:
                _add(vals, n * 1000)
    for rex in (_FULL_RE, _COMMA_RE):
        for m in rex.finditer(t):
            _add(vals, int(m.group(1).replace(",", "")))
    return sorted(vals)


def parse_posted_date(value: str) -> Optional[datetime]:
    """Best-effort parse of a posting date across source formats (ISO, epoch
    ms/s, YYYY-MM-DD). Returns None when unknown so callers don't over-filter."""
    s = (value or "").strip()
    if not s:
        return None
    if s.isdigit():
        ts = int(s)
        if ts > 10_000_000_000:  # epoch milliseconds (Lever)
            ts //= 1000
        try:
            return datetime.fromtimestamp(ts, tz=timezone.utc)
        except (ValueError, OSError):
            return None
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except ValueError:
        pass
    try:
        return datetime.strptime(s[:10], "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def _norm_company(s: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", (s or "").lower())).strip()


def required_min_years(text: str) -> Optional[int]:
    """Smallest 'years of experience' requirement mentioned near 'experien...'.

    Conservative: uses the most lenient figure so we rarely drop a viable role.
    """
    text_l = (text or "").lower()
    mins: List[int] = []
    for m in _YEARS_RE.finditer(text_l):
        pre = text_l[max(0, m.start() - 30):m.start()]
        post = text_l[m.start():m.end() + 50]
        if "experien" in pre or "experien" in post:
            mins.append(int(m.group(1)))
    return min(mins) if mins else None


def classify_location(raw: str, is_remote: bool = False) -> str:
    loc = (raw or "").lower()
    for alias in NY_ALIASES:
        if alias in loc:
            return "ny"
    for alias in SF_ALIASES:
        if alias in loc:
            return "sf"
    if is_remote or "remote" in loc:
        return "remote"
    return "other"


def suggest_ask(smin: Optional[int], smax: Optional[int], anchor: int = 100_000) -> int:
    """Desired-salary suggestion following the profile's rule:
      - no posted salary            -> anchor (e.g. $100k)
      - range below six figures     -> ask the top of their range (under $100k)
      - range reaching six figures  -> anchor floor, scaled up toward the top
    """
    if smax is None:
        return anchor
    if smax < anchor:
        return round_to(smax, 1000)
    midpoint = (smin + smax) // 2 if smin else smax
    return round_to(max(anchor, min(midpoint, smax)), 1000)


class Matcher:
    def __init__(self, profile: Profile):
        self.core = [p for p in profile.core_phrases if p]
        self.adjacent = [p for p in profile.adjacent_phrases if p]
        self.search = [p for p in profile.search_keywords if p]
        self.remote_ok = profile.remote_ok
        self.relocate = profile.willing_to_relocate
        self.experience_cap = profile.experience_cap
        self.salary_floor = profile.salary_floor
        self.salary_anchor = profile.salary_anchor
        self.exclude_companies = {_norm_company(c) for c in profile.exclude_companies}
        self.posted_within_days = profile.posted_within_days

        excludes = profile.exclude_keywords
        self.phd_check = any("phd" in e for e in excludes)
        self.exclude_phrases = [e for e in excludes if " " in e and "phd" not in e]
        self.exclude_words = [e for e in excludes if " " not in e]

        # meaningful tokens for the small per-token bonus
        self.tokens = set()
        for phrase in self.core + self.adjacent + self.search:
            for tok in re.split(r"[\s/]+", phrase):
                if len(tok) >= 3 and tok not in _STOPWORDS:
                    self.tokens.add(tok)

    # -- exclusion (title-based, precise) --
    def _title_excluded(self, title_l: str) -> Optional[str]:
        for phrase in self.exclude_phrases:
            if phrase in title_l:
                return f"excluded title phrase: '{phrase}'"
        for word in self.exclude_words:
            if re.search(r"\b" + re.escape(word) + r"\b", title_l):
                # 'manager' alone shouldn't drop entry titles like
                # 'Associate Product Manager'
                if word == "manager" and any(q in title_l for q in JUNIOR_QUALIFIERS):
                    continue
                return f"excluded seniority term: '{word}'"
        return None

    def evaluate(self, job: Job, strict_location: bool = False) -> Job:
        title_l = job.title.lower()
        blob = (job.title + "\n" + job.description).lower()

        # 1) Hard excludes -----------------------------------------------------
        reason = self._title_excluded(title_l)
        if reason:
            return self._reject(job, reason)
        if self.phd_check and _PHD_RE.search(blob):
            return self._reject(job, "requires a PhD")
        if self.exclude_companies and _norm_company(job.company) in self.exclude_companies:
            return self._reject(job, f"excluded company: {job.company}")

        # 2) Positive keyword score -------------------------------------------
        score = 0.0
        matched: List[str] = []
        for phrase in self.core:
            if phrase in title_l:
                score += 6; matched.append(phrase)
            elif phrase in blob:
                score += 3; matched.append(phrase)
        for phrase in self.adjacent:
            if phrase in title_l:
                score += 4; matched.append(phrase)
            elif phrase in blob:
                score += 2; matched.append(phrase)
        for kw in self.search:
            if kw in title_l:
                score += 3; matched.append(kw)
            elif kw in blob:
                score += 1; matched.append(kw)

        token_hits = sum(1 for t in self.tokens if re.search(r"\b" + re.escape(t) + r"\b", title_l))
        score += min(token_hits * 0.5, 3.0)

        job.matched = sorted(set(matched))
        if score <= 0:
            return self._reject(job, "no target-role/keyword match")

        # 3) Experience cap ----------------------------------------------------
        min_yrs = required_min_years(job.description)
        if min_yrs is not None and min_yrs > self.experience_cap:
            return self._reject(job, f"requires {min_yrs}+ yrs (> {self.experience_cap})")

        # 3b) Recency (optional; only filters when a date is known) ------------
        if self.posted_within_days:
            dt = parse_posted_date(job.posted_at)
            if dt is not None:
                age = (datetime.now(timezone.utc) - dt).days
                if age > self.posted_within_days:
                    return self._reject(job, f"stale ({age}d old > {self.posted_within_days}d)")

        # 4) Salary ------------------------------------------------------------
        sal = parse_salaries(job.salary_raw) or parse_salaries(job.description)
        if sal:
            job.salary_min, job.salary_max = min(sal), max(sal)
            if job.salary_max < self.salary_floor:
                return self._reject(
                    job, f"below floor (max ${job.salary_max // 1000}k < ${self.salary_floor // 1000}k)"
                )
        job.suggested_ask = suggest_ask(job.salary_min, job.salary_max, self.salary_anchor)

        # 5) Location (ranking; only filters in strict mode) -------------------
        is_remote = "remote" in job.location_raw.lower()
        bucket = classify_location(job.location_raw, is_remote)
        job.location_bucket = bucket
        loc_reason = None
        if bucket == "ny":
            score += 5; loc_reason = "NY metro (priority)"
        elif bucket == "sf":
            score += 4; loc_reason = "SF Bay Area"
        elif bucket == "remote":
            if self.remote_ok:
                score += 3; loc_reason = "Remote"
            else:
                bucket = "other"; job.location_bucket = "other"
        if bucket == "other":
            loc_reason = f"location: {job.location_raw or 'unspecified'}"
            if strict_location or not self.relocate:
                return self._reject(job, f"outside target locations ({job.location_raw or 'unknown'})")

        # 6) Finalize ----------------------------------------------------------
        reasons = [f"matches: {', '.join(job.matched[:6])}"]
        if loc_reason:
            reasons.append(loc_reason)
        if job.salary_max:
            reasons.append(f"salary {job.salary_display()} → suggest ${job.suggested_ask // 1000}k")
        job.reasons = reasons
        job.score = round(score, 1)
        job.rejected = False
        return job

    @staticmethod
    def _reject(job: Job, reason: str) -> Job:
        job.rejected = True
        job.reject_reason = reason
        return job
