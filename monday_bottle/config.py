"""Hard numbers for The Monday Bottle.

Every value the prose left fuzzy is pinned to a concrete number here. Where the
strategy gave an exact figure it is used verbatim; where it only gestured at a
threshold (e.g. "a clear margin above VWAP", "oversized") the number is a
DEFENSIBLE DEFAULT and is flagged with `# ASSUMPTION`. Change these in one place;
the whole engine and the tests follow.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    # --- Capital & sizing (verbatim from the spec) ---
    total_capital: float = 100.00
    spy_alloc: float = 50.00          # ~$50 SPY
    tqqq_alloc: float = 50.00         # ~$50 TQQQ
    fractional: bool = True
    cash_account: bool = True

    # --- VWAP "clear margin" buffer ---
    # "SPY must be above VWAP by a clear margin ... not hugging it tick-by-tick."
    # 10 bps (0.10%) of price. On a ~$600 SPY that's ~$0.60 of separation.
    vwap_buffer_bps: float = 10.0     # ASSUMPTION: spec said "clear margin", no number

    # --- VIX regime line (verbatim) ---
    vix_regime_line: float = 25.0     # > 25 => mean-reversion; < 25 => trend

    # --- Hard dollar floor (verbatim) ---
    hard_floor_pct: float = 0.15      # exit any leg down ~15%+ intraday, overrides technical stop

    # --- Gap classification ---
    spy_gap_sweet: float = 0.013      # +1.3% "sweet spot" (verbatim center)
    spy_gap_sweet_lo: float = 0.008   # ASSUMPTION: lower edge of the "sweet" band
    spy_gap_sweet_hi: float = 0.020   # ASSUMPTION: upper edge; bigger => "be more patient"
    tqqq_oversized_gap: float = 0.040  # ASSUMPTION: spec called ~+6% "oversized"; line drawn at +4%

    # --- Pre-market volume (verbatim) ---
    premarket_vol_institutional: float = 40_000_000  # 40M+ => institutions in

    # --- Order handling ---
    # "limit at or one cent through the ask" for marketable-limit buys.
    marketable_limit_through: float = 0.01
    time_in_force: str = "DAY"

    # --- Caps & locks (the two non-negotiables) ---
    rotation_cap: int = 1             # one rotation, load-bearing (anti-chop + cash settlement)
    reentry_cap: int = 1              # one TQQQ re-entry after a shake-out, then flat

    # --- Session clock (US/Eastern, 24h) ---
    tz: str = "America/New_York"
    read_time: str = "09:50"          # the only decision that matters
    soup_read_time: str = "09:55"     # widen the read on a structureless ("soup") open
    tqqq_late_arm: str = "10:15"      # reduced TQQQ entry deadline if no pullback came
    midday_no_add_start: str = "11:30"
    midday_no_add_end: str = "13:30"
    close_eval_time: str = "15:00"    # above/below VWAP at 3pm decides hold vs flatten
    bank_half_window_start: str = "15:45"  # ASSUMPTION: "final minutes" => last ~15 min
    no_new_rotation_after: str = "15:50"   # no new rotation in the last 10 minutes
    market_close: str = "16:00"


DEFAULT = Config()
