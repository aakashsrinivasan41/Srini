"""Experience-fit guardrail.

Parses a job description for required years of experience and over-qualification
signals so early-career candidates don't waste slots on 5y+/quant/senior-eng
roles. Returns a multiplier in [0,1] applied to the job's base score, plus a
human-readable reason.
"""
from __future__ import annotations

import re

# "5+ years", "5-7 years", "minimum of 5 years", "at least 5 years experience"
_YEARS = re.compile(
    r"(\d{1,2})\s*(?:\+|\s*-\s*\d{1,2})?\s*(?:or more\s*)?years?(?:\s+of)?"
    r"(?:\s+(?:relevant|professional|industry|work|hands-?on))?\s+experience",
    re.IGNORECASE,
)
# also catch "minimum of 5 years" / "at least 5 years" without trailing "experience"
_YEARS_LOOSE = re.compile(
    r"(?:minimum of|at least|min\.?)\s*(\d{1,2})\s*\+?\s*years?", re.IGNORECASE
)


def _max_required_years(text: str) -> int | None:
    found: list[int] = []
    for pat in (_YEARS, _YEARS_LOOSE):
        for m in pat.finditer(text):
            n = int(m.group(1))
            if 0 <= n <= 30:
                found.append(n)
    return max(found) if found else None


def fit(description: str, title: str, p: dict) -> tuple[float, str]:
    cfg = p.get("experience", {})
    if not cfg:
        return 1.0, ""
    text = f"{title}\n{description}".lower()

    req = _max_required_years(text)
    max_ok = cfg.get("max_required_years", 4)
    if req is not None and req > max_ok:
        return 0.05, f"requires {req}y experience (> {max_ok}y limit)"

    # over-qualification signals -> heavy penalty
    for sig in cfg.get("overqualified_signals", []):
        if sig.lower() in text:
            return 0.20, f"over-qualified signal: '{sig}'"

    # early-career signals -> small positive nudge
    nudge = 1.0
    for sig in cfg.get("earlycareer_signals", []):
        if sig.lower() in text:
            nudge = 1.08
            return min(nudge, 1.08), f"early-career fit: '{sig}'"

    return 1.0, "experience ok"
