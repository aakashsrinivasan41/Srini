"""Tiny HTML-to-text + number helpers (stdlib only)."""
from __future__ import annotations

import html
import re

_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")


def html_to_text(value: str | None) -> str:
    """Unescape HTML entities and strip tags. Greenhouse returns entity-encoded
    HTML in `content`, so unescape twice-safely then drop tags."""
    if not value:
        return ""
    text = html.unescape(value)
    text = _TAG_RE.sub(" ", text)
    text = html.unescape(text)  # in case entities were nested
    return _WS_RE.sub(" ", text).strip()


def round_to(value: float, step: int = 1000) -> int:
    """Round to the nearest `step` (used for salary suggestions)."""
    if step <= 0:
        return int(value)
    return int(round(value / step) * step)
