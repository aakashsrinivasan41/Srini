"""Load and normalize the user's profile + source configuration."""
from __future__ import annotations

import os
import re
from typing import List, Optional

try:
    import yaml
except ImportError as exc:  # pragma: no cover - friendly message
    raise SystemExit(
        "PyYAML is required. Install dependencies with:\n"
        "    pip install -r requirements.txt\n"
    ) from exc

# Profile filenames tried in priority order. profile.yaml/profile.local.yaml hold
# real data (gitignored); profile.example.yaml is the committed fallback so the
# tool runs out of the box for a demo.
PROFILE_CANDIDATES = ("profile.yaml", "profile.local.yaml", "profile.example.yaml")


class ProfileError(Exception):
    pass


def _normalize_phrases(items: List[str]) -> List[str]:
    """Split role names on '/', drop parentheticals, lowercase, dedupe.

    'Product Analyst / Associate Product Manager' -> ['product analyst',
    'associate product manager']; 'Quantitative Analyst (entry-level)' ->
    ['quantitative analyst'].
    """
    out: List[str] = []
    for raw in items or []:
        cleaned = re.sub(r"\([^)]*\)", " ", str(raw))  # strip parentheticals
        for part in cleaned.split("/"):
            phrase = re.sub(r"\s+", " ", part).strip().lower()
            if phrase and phrase not in out:
                out.append(phrase)
    return out


class Profile:
    """Typed-ish accessor over the raw profile dict."""

    def __init__(self, data: dict, path: str, name: str):
        self.data = data or {}
        self.path = path
        self.name = name
        self.is_example = name == "profile.example.yaml"

    # -- targeting --
    @property
    def core_phrases(self) -> List[str]:
        return _normalize_phrases((self.data.get("target_roles") or {}).get("core", []))

    @property
    def adjacent_phrases(self) -> List[str]:
        return _normalize_phrases((self.data.get("target_roles") or {}).get("adjacent", []))

    @property
    def search_keywords(self) -> List[str]:
        return [str(k).strip().lower() for k in (self.data.get("search_keywords") or []) if str(k).strip()]

    @property
    def exclude_keywords(self) -> List[str]:
        return [str(k).strip().lower() for k in (self.data.get("exclude_keywords") or []) if str(k).strip()]

    @property
    def exclude_companies(self) -> List[str]:
        return [str(c).strip() for c in (self.data.get("exclude_companies") or []) if str(c).strip()]

    @property
    def posted_within_days(self) -> Optional[int]:
        v = self.rules.get("posted_within_days")
        return int(v) if v else None

    # -- locations --
    @property
    def remote_ok(self) -> bool:
        return bool((self.data.get("locations") or {}).get("remote_ok", True))

    @property
    def willing_to_relocate(self) -> bool:
        return bool((self.data.get("locations") or {}).get("willing_to_relocate", True))

    # -- rules --
    @property
    def experience_cap(self) -> int:
        return int((self.rules.get("experience_cap_years", 3)))

    @property
    def rules(self) -> dict:
        return self.data.get("rules") or {}

    @property
    def salary_floor(self) -> int:
        return int((self.rules.get("salary") or {}).get("hard_floor_usd", 80000))

    @property
    def salary_anchor(self) -> int:
        return int((self.rules.get("salary") or {}).get("anchor_usd", 100000))

    def remotive_queries(self, limit: int) -> List[str]:
        """Keywords to feed the Remotive aggregator search."""
        return self.search_keywords[:limit]

    def info_sheet(self) -> str:
        """A human-readable summary of personal data for application packets."""
        d = self.data
        ident = d.get("identity") or {}
        auth = d.get("work_authorization") or {}
        eeo = d.get("eeo") or {}
        exp = d.get("experience") or {}
        loc = d.get("locations") or {}
        sal = self.rules.get("salary") or {}
        addr = ident.get("current_address") or {}
        L: List[str] = ["PERSONAL"]
        L.append(f"  Name:     {ident.get('full_name', '')}")
        L.append(f"  Email:    {ident.get('email', '')}")
        L.append(f"  Phone:    {ident.get('phone', '')}")
        if addr:
            L.append(f"  Address:  {addr.get('line1', '')}, {addr.get('city', '')}, "
                     f"{addr.get('state', '')} {addr.get('zip', '')}")
        if ident.get("linkedin"):
            L.append(f"  LinkedIn: {ident.get('linkedin')}")
        L += ["", "WORK AUTHORIZATION",
              f"  {auth.get('citizenship', '')}; sponsorship needed: "
              f"{'yes' if auth.get('require_sponsorship_now') else 'no'}"]
        L += ["", "EEO / SELF-ID (only if asked)",
              f"  Gender: {eeo.get('gender', '')} · Orientation: {eeo.get('sexual_orientation', '')}",
              f"  Race/Ethnicity: {eeo.get('race_ethnicity', '')} · "
              f"Hispanic/Latino: {'yes' if eeo.get('hispanic_or_latino') else 'no'}",
              f"  Veteran: {eeo.get('veteran_status', '')} · Disability: {eeo.get('disability_status', '')}"]
        L += ["", f"EXPERIENCE — {exp.get('total_years', '?')} yrs ({exp.get('level', '')})"]
        for w in d.get("work_history") or []:
            L.append(f"  • {w.get('company', '')} — {w.get('title', '')} — "
                     f"{w.get('location', '')} — {w.get('start', '')}–{w.get('end', '')}")
        L += ["", "EDUCATION"]
        for e in d.get("education") or []:
            gpa = f" (GPA {e.get('gpa')})" if e.get("gpa") else ""
            conc = f", {e.get('concentration')}" if e.get("concentration") else ""
            L.append(f"  • {e.get('school', '')} — {e.get('degree', '')}{conc} — {e.get('end', '')}{gpa}")
        pri = ", ".join(loc.get("priority", []))
        L += ["", f"LOCATIONS (priority): {pri} · relocate: "
              f"{'yes' if loc.get('willing_to_relocate') else 'no'} · "
              f"remote: {'yes' if loc.get('remote_ok') else 'no'}"]
        L += ["", "SALARY",
              f"  Floor: skip roles whose posted max is under ${int(sal.get('hard_floor_usd', 80000)) // 1000}k",
              f"  Desired-ask anchor ~${int(sal.get('anchor_usd', 100000)) // 1000}k "
              "(ask within range if low; scale up into six figures)"]
        L += ["", "RULES",
              "  No 'why this company' essays. If an essay is REQUIRED to submit → skip the application.",
              "  Stop before final submit for my review. Pause on login/CAPTCHA."]
        return "\n".join(L)


def find_profile_path(base_dir: str) -> tuple[str, str]:
    # Optional override (e.g. a shared install: JOB_RADAR_PROFILE=friend.yaml)
    override = os.environ.get("JOB_RADAR_PROFILE")
    if override:
        path = override if os.path.isabs(override) else os.path.join(base_dir, override)
        if os.path.exists(path):
            return path, os.path.basename(path)
        raise ProfileError(f"JOB_RADAR_PROFILE points to a missing file: {path}")
    for name in PROFILE_CANDIDATES:
        path = os.path.join(base_dir, name)
        if os.path.exists(path):
            return path, name
    raise ProfileError(
        f"No profile found in {base_dir}. Copy profile.example.yaml to profile.yaml."
    )


def load_profile(base_dir: str) -> Profile:
    path, name = find_profile_path(base_dir)
    with open(path, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    if not isinstance(data, dict):
        raise ProfileError(f"{path} did not parse to a mapping.")
    return Profile(data, path, name)


def load_sources(base_dir: str) -> dict:
    path = os.path.join(base_dir, "config", "sources.yaml")
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}
