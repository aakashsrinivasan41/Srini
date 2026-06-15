"""Tiny JSON persistence for SessionState so the locks/caps survive across the
separate CLI invocations you'll make through the trading day."""

from __future__ import annotations

import json
import os
from dataclasses import asdict

from .engine import SessionState

DEFAULT_PATH = os.path.join(os.getcwd(), ".monday_bottle_state.json")


def load(path: str = DEFAULT_PATH) -> SessionState:
    if not os.path.exists(path):
        return SessionState()
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    return SessionState(**data)


def save(state: SessionState, path: str = DEFAULT_PATH) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(asdict(state), fh, indent=2)


def reset(path: str = DEFAULT_PATH) -> None:
    if os.path.exists(path):
        os.remove(path)
