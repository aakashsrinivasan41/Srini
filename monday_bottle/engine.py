"""The decision engine: prose rules -> deterministic functions.

Each public function maps to a phase in the strategy. Functions are PURE
(no I/O, no clock reads except where a time string is passed in), so the tests
can drive every branch of the scenario matrix. Order placement lives in
broker.py; nothing here touches a network or an account.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from .config import Config, DEFAULT


# --------------------------------------------------------------------------- #
# Value objects
# --------------------------------------------------------------------------- #
@dataclass
class OrderTicket:
    """A concrete order to place. Until egress is opened, a human places it;
    afterwards broker.py maps it to the Robinhood MCP order tool."""
    side: str                       # "BUY" | "SELL"
    symbol: str                     # "SPY" | "TQQQ"
    notional: Optional[float] = None    # dollar amount (fractional)
    quantity: Optional[float] = None    # share/fractional-share count
    order_type: str = "MARKETABLE_LIMIT"
    limit_price: Optional[float] = None
    time_in_force: str = "DAY"
    note: str = ""

    def describe(self) -> str:
        size = f"${self.notional:.2f}" if self.notional is not None else f"{self.quantity} sh"
        px = f" @ {self.limit_price:.2f}" if self.limit_price is not None else ""
        return f"{self.side} {size} {self.symbol} [{self.order_type}{px}, {self.time_in_force}]"


@dataclass
class Decision:
    action: str                     # short machine token, e.g. "GO", "STAND_ASIDE", "EXIT_SPY"
    detail: str = ""                # human explanation
    orders: list[OrderTicket] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def __str__(self) -> str:
        lines = [f"ACTION: {self.action}", f"  why: {self.detail}"]
        for o in self.orders:
            lines.append(f"  order: {o.describe()}" + (f" -- {o.note}" if o.note else ""))
        for w in self.warnings:
            lines.append(f"  ! {w}")
        return "\n".join(lines)


@dataclass
class SessionState:
    """Persisted across CLI invocations so the locks/caps actually hold all day."""
    stood_aside: bool = False       # full-session lock once we stand aside at the read
    spy_in_position: bool = False
    tqqq_in_position: bool = False
    rotations_used: int = 0
    reentries_used: int = 0
    spy_entry_price: Optional[float] = None
    tqqq_entry_price: Optional[float] = None


# --------------------------------------------------------------------------- #
# Phase 1 — Gap gate
# --------------------------------------------------------------------------- #
@dataclass
class GapRead:
    spy_gap_pct: float
    tqqq_gap_pct: float
    vix: float
    premarket_vol: Optional[float]
    spy_class: str                  # "small" | "sweet" | "large"
    tqqq_oversized: bool
    institutions_in: Optional[bool]
    notes: list[str] = field(default_factory=list)


def classify_gap(spy_gap_pct: float, tqqq_gap_pct: float, vix: float,
                 premarket_vol: Optional[float] = None, cfg: Config = DEFAULT) -> GapRead:
    """Phase 1 (9:25-9:30). Classify the open. Informational — it does NOT enter;
    it sets posture for the 9:50 read. The bigger the gap, the more patient."""
    g = spy_gap_pct / 100.0 if abs(spy_gap_pct) > 1 else spy_gap_pct  # accept 1.3 or 0.013
    tg = tqqq_gap_pct / 100.0 if abs(tqqq_gap_pct) > 1 else tqqq_gap_pct
    notes: list[str] = []

    if g < cfg.spy_gap_sweet_lo:
        spy_class = "small"
        notes.append(f"SPY gap {g:+.2%} below sweet band ({cfg.spy_gap_sweet_lo:.2%}+) — thin edge.")
    elif g <= cfg.spy_gap_sweet_hi:
        spy_class = "sweet"
        notes.append(f"SPY gap {g:+.2%} in the sweet band — enter on the 9:50 signal.")
    else:
        spy_class = "large"
        notes.append(f"SPY gap {g:+.2%} is large — be MORE patient, never less. Let the range form.")

    oversized = tg >= cfg.tqqq_oversized_gap
    if oversized:
        notes.append(f"TQQQ gap {tg:+.2%} is oversized — do NOT chase; wait for a pullback that holds VWAP.")

    inst = None
    if premarket_vol is not None:
        inst = premarket_vol >= cfg.premarket_vol_institutional
        notes.append(("Pre-market volume institutional (40M+) — real participation."
                      if inst else "Pre-market volume light (<40M) — distrust the move."))

    if vix >= cfg.vix_regime_line:
        notes.append(f"VIX {vix:.1f} >= {cfg.vix_regime_line:.0f}: if it's sticky/elevated despite the gap, "
                     "the rally is hollow — quicker to bank, distrust breakouts.")

    return GapRead(g, tg, vix, premarket_vol, spy_class, oversized, inst, notes)


# --------------------------------------------------------------------------- #
# Regime from VIX
# --------------------------------------------------------------------------- #
@dataclass
class Regime:
    name: str                       # "trend" | "mean_reversion"
    hollow_rally_warning: bool
    detail: str


def regime_from_vix(vix: float, spy_gap_pct: float, cfg: Config = DEFAULT) -> Regime:
    g = spy_gap_pct / 100.0 if abs(spy_gap_pct) > 1 else spy_gap_pct
    if vix >= cfg.vix_regime_line:
        hollow = g > 0  # a relief-rally gap should crush VIX; if it didn't, suspect the rally
        return Regime(
            "mean_reversion", hollow,
            f"VIX {vix:.1f} >= {cfg.vix_regime_line:.0f}: mean-reversion regime — expect fades, "
            "be quicker to bank, distrust breakouts."
            + (" Gap up but VIX sticky => HOLLOW rally warning." if hollow else ""),
        )
    return Regime(
        "trend", False,
        f"VIX {vix:.1f} < {cfg.vix_regime_line:.0f}: trend regime — let it run.",
    )


# --------------------------------------------------------------------------- #
# Phase 3 — The 9:50 read (buffered)
# --------------------------------------------------------------------------- #
def _clearly_above(price: float, vwap: float, cfg: Config) -> bool:
    return price >= vwap * (1.0 + cfg.vwap_buffer_bps / 10_000.0)


def nine_fifty_read(spy_price: float, vwap: float, state: SessionState,
                    now: str = "09:50", cfg: Config = DEFAULT) -> Decision:
    """The only decision that matters. Buffered: clearly above VWAP => GO and enter
    SPY; at/below or merely hugging => STAND ASIDE for the FULL session (locked)."""
    if state.stood_aside:
        return Decision("STAND_ASIDE", "Full-session stand-aside lock is set. No re-entry, even on a reclaim.")
    if state.spy_in_position:
        return Decision("ALREADY_IN", "SPY position already open; this read has already fired.")

    if _clearly_above(spy_price, vwap, cfg):
        ticket = spy_entry(spy_price, cfg)
        return Decision(
            "GO",
            f"SPY {spy_price:.2f} is clearly above VWAP {vwap:.2f} "
            f"(buffer {cfg.vwap_buffer_bps:.0f}bps = {vwap * cfg.vwap_buffer_bps / 10_000.0:.2f}). "
            f"Enter SPY; arm TQQQ on the first pullback that holds VWAP.",
            orders=[ticket],
        )

    # at/below or hugging within the buffer
    state.stood_aside = True
    return Decision(
        "STAND_ASIDE",
        f"SPY {spy_price:.2f} is not clearly above VWAP {vwap:.2f} (within/under the "
        f"{cfg.vwap_buffer_bps:.0f}bps buffer). Stand aside for the FULL session. "
        "No late re-entry even if it reclaims later.",
        warnings=["Full-session stand-aside lock now SET."],
    )


def spy_entry(spy_price: float, cfg: Config = DEFAULT) -> OrderTicket:
    """Marketable-limit BUY of ~$50 SPY, limit one cent through (above) the price/ask."""
    return OrderTicket(
        side="BUY", symbol="SPY", notional=cfg.spy_alloc,
        order_type="MARKETABLE_LIMIT",
        limit_price=round(spy_price + cfg.marketable_limit_through, 2),
        time_in_force=cfg.time_in_force,
        note="~$50 leg; marketable limit 1c through to fill on liquidity but cap a wide-spread fill.",
    )


def tqqq_arm(tqqq_price: float, vwap: float, pullback_higher_low: bool,
             now: str, state: SessionState, cfg: Config = DEFAULT) -> Decision:
    """TQQQ is oversized, so it is NEVER chased at the read. Enter only on the first
    pullback that holds VWAP (a 5-min higher-low). If no pullback ever came but it is
    still clearly above VWAP by ~10:15, take a REDUCED entry on a 5-min higher-low.

    `pullback_higher_low` is an operator pattern-read: did the last 5-min bar make a
    higher low while holding above VWAP?
    """
    if state.stood_aside:
        return Decision("NO_TQQQ", "Stood aside for the session — no TQQQ leg.")
    if not _clearly_above(tqqq_price, vwap, cfg):
        return Decision("WAIT", f"TQQQ {tqqq_price:.2f} not clearly above VWAP {vwap:.2f}. No entry.")

    late = now >= cfg.tqqq_late_arm
    if pullback_higher_low:
        notional = cfg.tqqq_alloc * (0.5 if late else 1.0)
        ticket = OrderTicket(
            side="BUY", symbol="TQQQ", notional=round(notional, 2),
            order_type="MARKETABLE_LIMIT",
            limit_price=round(tqqq_price + cfg.marketable_limit_through, 2),
            time_in_force=cfg.time_in_force,
            note=("REDUCED late entry (no pullback came, >=10:15)" if late
                  else "First pullback held VWAP (5-min higher-low)"),
        )
        return Decision("ENTER_TQQQ", ticket.note + ".", orders=[ticket])

    if late:
        return Decision("NO_TQQQ",
                        f"Past {cfg.tqqq_late_arm} with no higher-low confirmation. Skip the TQQQ leg; hold SPY.")
    return Decision("WAIT", "Above VWAP but no 5-min higher-low yet. Wait for the pullback to hold.")


# --------------------------------------------------------------------------- #
# Phase 4 — Management (stops are mental/manual, evaluated on 5-min closes)
# --------------------------------------------------------------------------- #
def _hard_floor_hit(entry: Optional[float], current: float, cfg: Config) -> bool:
    if entry is None or entry <= 0:
        return False
    return (current - entry) / entry <= -cfg.hard_floor_pct


def manage_spy(five_min_close: float, vwap: float, current_price: float,
               state: SessionState, cfg: Config = DEFAULT) -> Decision:
    """SPY stop = VWAP: one 5-min CLOSE below VWAP with no reclaim => out. The hard
    -15% dollar floor overrides intrabar (a violent air-pocket need not wait for a close)."""
    if not state.spy_in_position:
        return Decision("NONE", "No SPY position to manage.")

    if _hard_floor_hit(state.spy_entry_price, current_price, cfg):
        return Decision("EXIT_SPY",
                        f"HARD FLOOR: SPY {current_price:.2f} is >= {cfg.hard_floor_pct:.0%} below entry "
                        f"{state.spy_entry_price:.2f}. Disorderly air-pocket overrides the VWAP stop — exit now.",
                        orders=[_flat("SPY", state, cfg)],
                        warnings=["Dollar-floor override: do not wait for the 5-min close."])

    if five_min_close < vwap:
        return Decision("EXIT_SPY",
                        f"5-min close {five_min_close:.2f} below VWAP {vwap:.2f}, no reclaim. "
                        "VWAP stop hit — exit SPY.",
                        orders=[_flat("SPY", state, cfg)])

    return Decision("HOLD_SPY", f"5-min close {five_min_close:.2f} holds at/above VWAP {vwap:.2f}. Hold.")


def manage_tqqq(five_min_close: float, or_low: float, current_price: float,
                state: SessionState, cfg: Config = DEFAULT) -> Decision:
    """TQQQ stop = opening-range low (structural; absorbs 3x VWAP noise). Same hard
    -15% floor override."""
    if not state.tqqq_in_position:
        return Decision("NONE", "No TQQQ position to manage.")

    if _hard_floor_hit(state.tqqq_entry_price, current_price, cfg):
        return Decision("EXIT_TQQQ",
                        f"HARD FLOOR: TQQQ {current_price:.2f} is >= {cfg.hard_floor_pct:.0%} below entry "
                        f"{state.tqqq_entry_price:.2f}. Exit now — disorderly move overrides the ORL stop.",
                        orders=[_flat("TQQQ", state, cfg)],
                        warnings=["Dollar-floor override: do not wait for the 5-min close."])

    if five_min_close < or_low:
        return Decision("EXIT_TQQQ",
                        f"5-min close {five_min_close:.2f} below opening-range low {or_low:.2f}. "
                        "Structural stop hit — exit TQQQ.",
                        orders=[_flat("TQQQ", state, cfg)])

    return Decision("HOLD_TQQQ", f"5-min close {five_min_close:.2f} holds above ORL {or_low:.2f}. Hold.")


def _flat(symbol: str, state: SessionState, cfg: Config) -> OrderTicket:
    return OrderTicket(side="SELL", symbol=symbol, order_type="MARKETABLE_LIMIT",
                       time_in_force=cfg.time_in_force, note="Close the whole leg.")


# --------------------------------------------------------------------------- #
# Phase 5 — The swing (one rotation, hard-capped)
# --------------------------------------------------------------------------- #
def swing_rotation(spy_in_profit: bool, pullback_held_vwap: bool, broke_prior_swing_high: bool,
                   volume_confirms: bool, now: str, breakout_level: float,
                   state: SessionState, cfg: Config = DEFAULT) -> Decision:
    """Swing-on-strength: SPY in profit -> pulls back -> holds VWAP (higher low) ->
    breaks the pre-pullback swing high ON VOLUME -> bank SPY, deploy proceeds into TQQQ,
    stop at the breakout level / VWAP. Hard-capped at ONE rotation (anti-chop AND a cash
    settlement guardrail). The pattern reads are operator-supplied."""
    if state.rotations_used >= cfg.rotation_cap:
        return Decision("NO_ROTATION",
                        f"Rotation cap reached ({state.rotations_used}/{cfg.rotation_cap}). "
                        "This cap is load-bearing twice: anti-chop AND cash-settlement. Do not exceed.")
    if now >= cfg.no_new_rotation_after:
        return Decision("NO_ROTATION", f"Past {cfg.no_new_rotation_after} — no new rotation in the last 10 minutes.")
    if not state.spy_in_position:
        return Decision("NO_ROTATION", "No SPY position to rotate from.")
    if not (spy_in_profit and pullback_held_vwap and broke_prior_swing_high and volume_confirms):
        missing = [n for n, ok in (("in-profit", spy_in_profit), ("held-VWAP-on-pullback", pullback_held_vwap),
                                    ("broke-prior-swing-high", broke_prior_swing_high),
                                    ("volume-confirms", volume_confirms)) if not ok]
        return Decision("WAIT", f"Swing not confirmed (missing: {', '.join(missing)}). "
                                "If it just grinds up VWAP, do nothing and ride to close.")

    sell = OrderTicket(side="SELL", symbol="SPY", order_type="MARKETABLE_LIMIT",
                       time_in_force=cfg.time_in_force, note="Bank SPY to fund the rotation.")
    buy = OrderTicket(side="BUY", symbol="TQQQ", notional=cfg.spy_alloc, order_type="MARKETABLE_LIMIT",
                      time_in_force=cfg.time_in_force,
                      note=f"Deploy SPY proceeds into TQQQ; stop at breakout level {breakout_level:.2f}/VWAP.")
    return Decision("ROTATE_TO_TQQQ",
                    "Confirmed second leg: bank SPY, lever into TQQQ, stop at breakout/VWAP. "
                    "This consumes the one allowed rotation.",
                    orders=[sell, buy],
                    warnings=["Now fully concentrated in TQQQ: ORL stop and the -15% floor are the ONLY guards."])


def reentry_after_shakeout(spy_was_stopped: bool, reclaimed_vwap_two_closes: bool,
                           tqqq_price: float, vwap: float, now: str,
                           state: SessionState, cfg: Config = DEFAULT) -> Decision:
    """After SPY stops (loss/BE), if price reclaims VWAP and holds 2 consecutive 5-min
    closes, take ONE TQQQ entry, stop below VWAP. If that stops too => flat, done."""
    if state.reentries_used >= cfg.reentry_cap:
        return Decision("NO_REENTRY", f"Re-entry cap reached ({state.reentries_used}/{cfg.reentry_cap}). Flat, done.")
    if state.rotations_used >= cfg.rotation_cap:
        return Decision("NO_REENTRY", "Rotation budget already spent (settlement + sanity). Flat, done.")
    if now >= cfg.no_new_rotation_after:
        return Decision("NO_REENTRY", f"Past {cfg.no_new_rotation_after} — no new entries in the last 10 minutes.")
    if not (spy_was_stopped and reclaimed_vwap_two_closes):
        return Decision("WAIT", "Need SPY stopped AND VWAP reclaimed on 2 consecutive 5-min closes first.")

    buy = OrderTicket(side="BUY", symbol="TQQQ", notional=cfg.tqqq_alloc, order_type="MARKETABLE_LIMIT",
                      limit_price=round(tqqq_price + cfg.marketable_limit_through, 2),
                      time_in_force=cfg.time_in_force, note="One re-entry; stop below VWAP. Stops again => flat.")
    return Decision("REENTER_TQQQ",
                    f"VWAP reclaimed on 2 closes after the shake-out. One TQQQ re-entry, stop below VWAP {vwap:.2f}.",
                    orders=[buy], warnings=["This is the LAST attempt. If it stops, you are flat for the day."])


# --------------------------------------------------------------------------- #
# Phase 6 — Close
# --------------------------------------------------------------------------- #
def close_phase(spy_above_vwap_at_3pm: bool, now: str,
                state: SessionState, cfg: Config = DEFAULT) -> Decision:
    """At 3pm: above VWAP => hold/trail tighter, bank HALF the leveraged (TQQQ) leg in
    the final minutes. Below VWAP => flatten all, no overnight, no late rotation."""
    if not spy_above_vwap_at_3pm:
        orders = []
        if state.spy_in_position:
            orders.append(_flat("SPY", state, cfg))
        if state.tqqq_in_position:
            orders.append(_flat("TQQQ", state, cfg))
        return Decision("FLATTEN_ALL",
                        "Below VWAP at 3pm. Flatten everything. No overnight, no last-10-min rotation.",
                        orders=orders)

    orders = []
    note = "Hold and trail tighter into the last 15 minutes."
    if state.tqqq_in_position and now >= cfg.bank_half_window_start:
        orders.append(OrderTicket(side="SELL", symbol="TQQQ", order_type="MARKETABLE_LIMIT",
                                  time_in_force=cfg.time_in_force,
                                  note="Bank HALF the TQQQ leg — lock the torque gain, let half run."))
        note = "Final minutes: bank half the TQQQ leg, let the other half run; trail the rest."
    return Decision("HOLD_AND_TRAIL", "Above VWAP at 3pm. " + note, orders=orders)
