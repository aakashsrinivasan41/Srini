"""Experience-fit guardrail.

Parses a job description for required years of experience and over-qualification
signals so early-career candidates don't waste slots on 5y+/quant/senior-eng
roles. Returns a multiplier in [0,1] applied to the job's base score, plus a
human-readable reason.
"""
from __future__ import annotations

import re

# Range-aware. For "2-5 years" we capture the LOWER bound (2) — you only need
# to clear the floor of a range. For "4+ years" we capture 4. Then we take the
# MAX lower-bound across all experience mentions, so a role asking "4+ yrs total
# incl. 2+ yrs presales" is read as 4 (the binding requirement), while a single
# "2-5 yrs" range is read as 2 (you're in range -> keep).
_YEARS_EXP = re.compile(
    r"(\d{1,2})\s*(?:[-–—]\s*\d{1,2})?\s*\+?\s*(?:or more\s*)?years?(?:\s+of)?"
    r"(?:\s+\w+){0,3}?\s+experience",
    re.IGNORECASE,
)
# "minimum of 5 years" / "at least 5 years" without a trailing "experience"
_YEARS_LOOSE = re.compile(
    r"(?:minimum of|at least|min\.?|minimum)\s*(\d{1,2})\s*\+?\s*years?", re.IGNORECASE
)


def _max_required_years(text: str) -> int | None:
    """Highest binding years-of-experience requirement, or None.

    group(1) is always the lower bound of a range (or the bare number), so a
    "2-5 years" range contributes 2, not 5.
    """
    found: list[int] = []
    for pat in (_YEARS_EXP, _YEARS_LOOSE):
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
