"""Load and normalize the user's profile + source configuration."""
from __future__ import annotations

import os
import re
from typing import List

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


def find_profile_path(base_dir: str) -> tuple[str, str]:
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
