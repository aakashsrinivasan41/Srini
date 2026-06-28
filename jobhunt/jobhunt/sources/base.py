"""Shared HTTP helper with retry + sane timeouts + a real UA."""
from __future__ import annotations

import time
from typing import Any, Optional

import requests

UA = "jobhunt/0.1 (+personal job-search aggregator; respects robots/ToS)"
TIMEOUT = 25


def get_json(url: str, *, method: str = "GET", params: Optional[dict] = None,
             retries: int = 3, backoff: float = 2.0) -> Any:
    """Fetch JSON with exponential backoff on network/5xx errors.

    Raises requests.HTTPError on a final 4xx (e.g. a bad slug -> 404) so the
    caller can report 'company not found on this ATS' cleanly.
    """
    last_exc: Optional[Exception] = None
    for attempt in range(retries):
        try:
            resp = requests.request(
                method, url, params=params,
                headers={"User-Agent": UA, "Accept": "application/json"},
                timeout=TIMEOUT,
            )
            if resp.status_code >= 500:
                raise requests.HTTPError(f"{resp.status_code} server error", response=resp)
            resp.raise_for_status()
            return resp.json()
        except (requests.ConnectionError, requests.Timeout, requests.HTTPError) as e:
            # don't retry a definitive 4xx (bad slug / not found)
            status = getattr(getattr(e, "response", None), "status_code", None)
            if status and 400 <= status < 500:
                raise
            last_exc = e
            if attempt < retries - 1:
                time.sleep(backoff * (2 ** attempt))
    raise last_exc  # type: ignore[misc]
