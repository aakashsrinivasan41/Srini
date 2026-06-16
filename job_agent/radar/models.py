"""The normalized Job record shared across sources, matching, state and report."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Job:
    # --- raw fields populated by sources ---
    source: str
    company: str
    title: str
    url: str
    location_raw: str = ""
    description: str = ""
    salary_raw: str = ""
    posted_at: str = ""
    external_id: str = ""

    # --- computed by the matcher ---
    location_bucket: str = "other"      # ny | sf | remote | other
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    suggested_ask: Optional[int] = None
    score: float = 0.0
    matched: List[str] = field(default_factory=list)
    reasons: List[str] = field(default_factory=list)
    rejected: bool = False
    reject_reason: str = ""

    @property
    def key(self) -> str:
        """Stable de-dup key. Prefer the URL; fall back to source+id."""
        basis = self.url.strip().lower() or f"{self.source}:{self.external_id}"
        return hashlib.sha1(basis.encode("utf-8")).hexdigest()[:16]

    def salary_display(self) -> str:
        if self.salary_min and self.salary_max and self.salary_min != self.salary_max:
            return f"${self.salary_min // 1000}k–${self.salary_max // 1000}k"
        if self.salary_max:
            return f"${self.salary_max // 1000}k"
        if self.salary_raw:
            return self.salary_raw.strip()[:40]
        return "—"

    def to_row(self) -> dict:
        """Flatten for SQLite storage."""
        return {
            "key": self.key,
            "source": self.source,
            "company": self.company,
            "title": self.title,
            "url": self.url,
            "location_raw": self.location_raw,
            "location_bucket": self.location_bucket,
            "salary_min": self.salary_min,
            "salary_max": self.salary_max,
            "suggested_ask": self.suggested_ask,
            "score": self.score,
            "matched": json.dumps(self.matched),
            "reasons": json.dumps(self.reasons),
            "posted_at": self.posted_at,
        }
