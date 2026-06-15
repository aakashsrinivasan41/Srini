"""The Monday Bottle — a deterministic decision engine for the hardened day-one strategy.

This package turns the prose strategy into hard-numbered, testable rules.

Division of responsibility (read this before trusting it with money):

  * The ENGINE owns every non-negotiable, mechanical rule: the VWAP buffer,
    the VIX regime line, the hard -15% dollar floor, the full-session
    stand-aside lock, and the one-rotation cap. These cannot be fat-fingered.

  * YOU (or, later, a market-data feed) supply the live numbers the engine
    cannot see on its own: prices, VWAP, VIX, the opening range, and a small
    number of explicit *pattern reads* (e.g. "did the pullback make a 5-min
    higher low?") that require looking at a chart the engine does not have.

  * Order PLACEMENT is intentionally NOT wired to a live broker here. The
    Robinhood trading MCP is network-blocked from this environment, so
    broker.py emits concrete order tickets for a human to place and marks the
    one spot where a real MCP order call must be substituted once egress is
    opened. Nothing in this package can move real money by itself.
"""

from .config import Config, DEFAULT
from .engine import (
    Decision,
    OrderTicket,
    SessionState,
    classify_gap,
    regime_from_vix,
    nine_fifty_read,
    spy_entry,
    tqqq_arm,
    manage_spy,
    manage_tqqq,
    swing_rotation,
    reentry_after_shakeout,
    close_phase,
)

__all__ = [
    "Config",
    "DEFAULT",
    "Decision",
    "OrderTicket",
    "SessionState",
    "classify_gap",
    "regime_from_vix",
    "nine_fifty_read",
    "spy_entry",
    "tqqq_arm",
    "manage_spy",
    "manage_tqqq",
    "swing_rotation",
    "reentry_after_shakeout",
    "close_phase",
]
