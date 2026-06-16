"""Dependency-free HTTP helpers (stdlib urllib) with retries + backoff."""
from __future__ import annotations

import json
import socket
import time
import urllib.error
import urllib.request

DEFAULT_TIMEOUT = 20
USER_AGENT = "job-radar/1.0 (+personal job-search assistant)"
# A realistic browser UA, used only for public HTML endpoints that reject
# non-browser agents (e.g. LinkedIn's guest job pages).
BROWSER_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
_RETRYABLE = {429, 500, 502, 503, 504}


class FetchError(Exception):
    """Raised on any network/HTTP/JSON failure so callers can skip gracefully."""


def _request(url: str, timeout: int, headers: dict | None, retries: int, backoff: float) -> bytes:
    req_headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    if headers:
        req_headers.update(headers)
    req = urllib.request.Request(url, headers=req_headers)
    last_err = "unknown error"
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read()
        except urllib.error.HTTPError as exc:
            last_err = f"HTTP {exc.code}"
            if exc.code in _RETRYABLE and attempt < retries:
                time.sleep(backoff * (2 ** attempt))
                continue
            raise FetchError(f"{last_err} for {url}") from exc
        except (urllib.error.URLError, socket.timeout, OSError) as exc:
            last_err = f"network error: {exc}"
            if attempt < retries:
                time.sleep(backoff * (2 ** attempt))
                continue
            raise FetchError(f"{last_err} for {url}") from exc
    raise FetchError(f"{last_err} for {url}")


def get_json(url: str, timeout: int = DEFAULT_TIMEOUT, headers: dict | None = None,
             retries: int = 2, backoff: float = 1.5):
    raw = _request(url, timeout, headers, retries, backoff)
    try:
        return json.loads(raw.decode("utf-8", errors="replace"))
    except json.JSONDecodeError as exc:
        raise FetchError(f"invalid JSON from {url}: {exc}") from exc


def get_text(url: str, timeout: int = DEFAULT_TIMEOUT, headers: dict | None = None,
             retries: int = 2, backoff: float = 1.5) -> str:
    raw = _request(url, timeout, headers, retries, backoff)
    return raw.decode("utf-8", errors="replace")
