"""Order routing.

IMPORTANT: This does NOT place live orders. The Robinhood trading MCP host
(`agent.robinhood.com`) is blocked by this environment's network egress policy,
so there is no way to reach the account from here. Until that host is allowlisted
and a fresh, authenticated session is started, the only safe and honest behaviour
is to print the exact order ticket for a human to place by hand.

When egress IS opened, the ONE function to change is `place()`: replace the
`DRY_RUN` branch with a real call to the Robinhood MCP order tool. The tool's
exact name and argument schema are not yet known (the schema only loads after
OAuth, which is currently blocked), so the live branch is intentionally left as
an explicit, un-guessed TODO rather than a fabricated call that might mis-route a
real order.
"""

from __future__ import annotations

from .engine import Decision, OrderTicket


DRY_RUN = True  # flip to False ONLY in an authenticated session with egress open


def place(ticket: OrderTicket) -> str:
    if DRY_RUN:
        return f"[DRY-RUN — PLACE BY HAND] {ticket.describe()}" + (f"  ({ticket.note})" if ticket.note else "")

    # --- LIVE BRANCH (do not enable until verified) -------------------------
    # Once authenticated, inspect the Robinhood MCP order tool's real schema and
    # map this ticket onto it, e.g. something shaped like:
    #
    #   mcp__robinhood-trading__place_order(
    #       symbol=ticket.symbol,
    #       side=ticket.side.lower(),
    #       amount_in_dollars=ticket.notional,        # fractional/notional buys
    #       quantity=ticket.quantity,                 # or share count
    #       type="limit" if ticket.limit_price else "market",
    #       limit_price=ticket.limit_price,
    #       time_in_force=ticket.time_in_force.lower(),
    #   )
    #
    # The exact names above are PLACEHOLDERS. Verify them against the live tool
    # schema before sending a single order. Failing closed on purpose:
    raise NotImplementedError(
        "Live order routing is not wired. Verify the Robinhood MCP order-tool "
        "schema in an authenticated session, then implement this branch."
    )


def execute(decision: Decision) -> list[str]:
    """Render every order in a decision through `place`."""
    return [place(o) for o in decision.orders]
