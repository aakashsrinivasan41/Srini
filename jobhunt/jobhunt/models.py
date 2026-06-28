"""Shared data structures and config loading."""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import yaml

CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_yaml(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_profile() -> dict:
    return load_yaml(CONFIG_DIR / "profile.yaml")


def load_companies() -> dict:
    return load_yaml(CONFIG_DIR / "companies.yaml")


@dataclass
class Job:
    """Normalized posting shape produced by every source adapter."""

    source: str                 # greenhouse | lever | ashby
    company: str
    title: str
    location: str
    url: str                    # canonical posting / apply URL
    job_id: str = ""
    department: str = ""
    remote: Optional[bool] = None
    employment_type: str = ""
    comp_min: Optional[int] = None
    comp_max: Optional[int] = None
    description: str = ""        # plain text, best-effort
    posted_at: str = ""
    # populated downstream
    score: float = 0.0
    score_breakdown: dict = field(default_factory=dict)

    @property
    def fingerprint(self) -> str:
        """Stable id for dedupe across sources/runs."""
        basis = f"{self.company.lower()}|{self.title.lower()}|{normalize_loc(self.location)}"
        return hashlib.sha1(basis.encode()).hexdigest()[:16]

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Job":
        known = {k: v for k, v in d.items() if k in cls.__dataclass_fields__}
        return cls(**known)


# --- small text helpers reused across modules -------------------------------

_WS = re.compile(r"\s+")
_TAGS = re.compile(r"<[^>]+>")


def strip_html(s: str) -> str:
    if not s:
        return ""
    s = _TAGS.sub(" ", s)
    s = (
        s.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
        .replace("&#39;", "'").replace("&quot;", '"').replace("&nbsp;", " ")
    )
    return _WS.sub(" ", s).strip()


def normalize_loc(s: str) -> str:
    return _WS.sub(" ", (s or "").lower()).strip()


# Detect "$120,000 - $150,000" / "$120k" style ranges anywhere in text.
_MONEY = re.compile(r"\$\s?(\d{2,3})(?:,(\d{3}))?(?:\.\d+)?\s*([kK])?")


def parse_date(s: str) -> Optional[datetime]:
    """Best-effort parse of the many date shapes the boards emit.

    Handles: ISO 8601 (Greenhouse/Ashby), epoch seconds/millis (Lever),
    plain dates, and fuzzy 'posted N days/weeks ago' strings (some Apify
    actors). Returns a tz-aware UTC datetime, or None if unparseable.
    """
    if not s:
        return None
    s = str(s).strip()

    # epoch (Lever uses millis)
    if s.isdigit():
        n = int(s)
        if n > 1_000_000_000_000:
            n //= 1000
        try:
            return datetime.fromtimestamp(n, tz=timezone.utc)
        except (ValueError, OSError):
            return None

    # "3 days ago" / "2 weeks ago" / "today" / "yesterday"
    rel = s.lower()
    if "today" in rel or "just posted" in rel or "hour" in rel or "minute" in rel:
        return datetime.now(timezone.utc)
    if "yesterday" in rel:
        return datetime.now(timezone.utc) - _delta(days=1)
    m = re.search(r"(\d+)\+?\s*(day|week|month)", rel)
    if m and "ago" in rel:
        n = int(m.group(1))
        unit = m.group(2)
        days = n * {"day": 1, "week": 7, "month": 30}[unit]
        return datetime.now(timezone.utc) - _delta(days=days)

    # ISO 8601
    try:
        d = datetime.fromisoformat(s.replace("Z", "+00:00"))
        return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
    except ValueError:
        pass

    # common explicit formats
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y", "%b %d, %Y", "%B %d, %Y", "%d %b %Y"):
        try:
            return datetime.strptime(s, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def _delta(days: int):
    from datetime import timedelta
    return timedelta(days=days)


def age_days(s: str) -> Optional[int]:
    """Days since the posting date, or None if unknown."""
    d = parse_date(s)
    if not d:
        return None
    days = (datetime.now(timezone.utc) - d).days
    return max(days, 0)


def parse_comp(text: str) -> tuple[Optional[int], Optional[int]]:
    """Best-effort salary extraction. Returns (min, max) annual USD or (None, None)."""
    if not text:
        return None, None
    vals: list[int] = []
    for m in _MONEY.finditer(text):
        whole, thousands, k = m.group(1), m.group(2), m.group(3)
        if thousands:
            n = int(whole + thousands)
        elif k:
            n = int(whole) * 1000
        else:
            # bare 2-3 digit number with no k and no thousands -> likely "$120" meaning 120k in comp context
            n = int(whole) * 1000
        # plausibility filter for annual salaries
        if 30000 <= n <= 1000000:
            vals.append(n)
    if not vals:
        return None, None
    return min(vals), max(vals)
