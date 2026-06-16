"""SQLite-backed state: de-dupe across runs and track application status."""
from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone
from typing import List

from .models import Job

OPEN_STATUSES = ("new", "seen")
ALL_STATUSES = ("new", "seen", "applied", "skipped", "hidden")

_SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    key            TEXT PRIMARY KEY,
    source         TEXT,
    company        TEXT,
    title          TEXT,
    url            TEXT,
    location_raw   TEXT,
    location_bucket TEXT,
    salary_min     INTEGER,
    salary_max     INTEGER,
    suggested_ask  INTEGER,
    score          REAL,
    matched        TEXT,
    reasons        TEXT,
    posted_at      TEXT,
    status         TEXT NOT NULL DEFAULT 'new',
    first_seen     TEXT,
    last_seen      TEXT
);
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Store:
    def __init__(self, db_path: str):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(_SCHEMA)
        self.conn.commit()

    def close(self):
        self.conn.close()

    def upsert(self, jobs: List[Job]) -> dict:
        """Insert new jobs / refresh existing ones. Never resurfaces jobs the
        user has already actioned (applied/skipped/hidden)."""
        new_count = updated = 0
        now = _now()
        for job in jobs:
            row = job.to_row()
            existing = self.conn.execute(
                "SELECT status FROM jobs WHERE key = ?", (row["key"],)
            ).fetchone()
            if existing is None:
                self.conn.execute(
                    """INSERT INTO jobs
                       (key, source, company, title, url, location_raw, location_bucket,
                        salary_min, salary_max, suggested_ask, score, matched, reasons,
                        posted_at, status, first_seen, last_seen)
                       VALUES (:key,:source,:company,:title,:url,:location_raw,:location_bucket,
                        :salary_min,:salary_max,:suggested_ask,:score,:matched,:reasons,
                        :posted_at,'new',:first_seen,:last_seen)""",
                    {**row, "first_seen": now, "last_seen": now},
                )
                new_count += 1
            else:
                # refresh score/fields + last_seen; demote 'new' -> 'seen' only on
                # a later run is handled by mark_surfaced(); here we keep status.
                self.conn.execute(
                    """UPDATE jobs SET score=:score, matched=:matched, reasons=:reasons,
                       salary_min=:salary_min, salary_max=:salary_max,
                       suggested_ask=:suggested_ask, location_bucket=:location_bucket,
                       last_seen=:last_seen WHERE key=:key""",
                    {**row, "last_seen": now},
                )
                updated += 1
        self.conn.commit()
        return {"new": new_count, "updated": updated}

    def fetch(self, statuses=OPEN_STATUSES, min_score: float = 0.0, source: str | None = None):
        q = "SELECT * FROM jobs WHERE status IN (%s) AND score >= ?" % (
            ",".join("?" * len(statuses))
        )
        params = list(statuses) + [min_score]
        if source:
            q += " AND source = ?"
            params.append(source)
        q += " ORDER BY (status='new') DESC, score DESC, company ASC"
        return [dict(r) for r in self.conn.execute(q, params).fetchall()]

    def set_status(self, key: str, status: str) -> bool:
        if status not in ALL_STATUSES:
            raise ValueError(f"invalid status '{status}' (use {ALL_STATUSES})")
        cur = self.conn.execute("UPDATE jobs SET status=? WHERE key=?", (status, key))
        self.conn.commit()
        return cur.rowcount > 0

    def demote_new_to_seen(self):
        """Call after a report is generated so 'new' highlights only fresh finds."""
        self.conn.execute("UPDATE jobs SET status='seen' WHERE status='new'")
        self.conn.commit()

    def counts(self) -> dict:
        rows = self.conn.execute(
            "SELECT status, COUNT(*) c FROM jobs GROUP BY status"
        ).fetchall()
        return {r["status"]: r["c"] for r in rows}


def row_matched(row: dict) -> list:
    try:
        return json.loads(row.get("matched") or "[]")
    except json.JSONDecodeError:
        return []


def row_reasons(row: dict) -> list:
    try:
        return json.loads(row.get("reasons") or "[]")
    except json.JSONDecodeError:
        return []
