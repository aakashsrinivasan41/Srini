"""Small, dependency-free HTTP helper (stdlib urllib only)."""
from __future__ import annotations

import json
import socket
import urllib.error
import urllib.request

DEFAULT_TIMEOUT = 20
USER_AGENT = "job-radar/1.0 (+personal job-search assistant)"


class FetchError(Exception):
    """Raised on any network/HTTP/JSON failure so callers can skip gracefully."""


def get_json(url: str, timeout: int = DEFAULT_TIMEOUT, headers: dict | None = None):
    """GET a URL and parse JSON. Raises FetchError on any problem."""
    req_headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
    }
    if headers:
        req_headers.update(headers)
    req = urllib.request.Request(url, headers=req_headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
    except urllib.error.HTTPError as exc:
        raise FetchError(f"HTTP {exc.code} for {url}") from exc
    except (urllib.error.URLError, socket.timeout, OSError) as exc:
        raise FetchError(f"network error for {url}: {exc}") from exc
    try:
        return json.loads(raw.decode("utf-8", errors="replace"))
    except json.JSONDecodeError as exc:
        raise FetchError(f"invalid JSON from {url}: {exc}") from exc
