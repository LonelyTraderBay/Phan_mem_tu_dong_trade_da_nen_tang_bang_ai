"""Prod-live capital envelope (≤5% NAV) + live venue gate.

Owner LIVE-VENUE-ADAPTER: LIVE_NAV_QUOTE=100000 → max notional 5000 at 5%.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


DEFAULT_MAX_NAV_PCT = 5.0


class LiveCapitalError(Exception):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)


@dataclass(frozen=True)
class LiveCapitalPolicy:
    max_nav_pct: float
    nav_quote: float | None
    max_notional: float | None
    live_trading_enabled: bool
    phase2_gates_ack: bool
    live_venue_mode: str


def _env_bool(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes", "on")


def _env_float(name: str) -> float | None:
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return None
    return float(raw)


def get_live_venue_mode() -> str:
    mode = os.environ.get("LIVE_VENUE_MODE", "").strip().lower()
    if mode in ("binance_mainnet", "off", ""):
        return mode or "off"
    return "off"


def load_policy() -> LiveCapitalPolicy:
    raw_pct = _env_float("LIVE_MAX_NAV_PCT")
    max_pct = clamp_max_nav_pct(raw_pct if raw_pct is not None else DEFAULT_MAX_NAV_PCT)

    nav = _env_float("LIVE_NAV_QUOTE")
    max_notional = None
    if nav is not None and nav > 0:
        max_notional = nav * (max_pct / 100.0)

    return LiveCapitalPolicy(
        max_nav_pct=max_pct,
        nav_quote=nav,
        max_notional=max_notional,
        live_trading_enabled=_env_bool("LIVE_TRADING_ENABLED", False),
        phase2_gates_ack=_env_bool("PHASE2_GATES_ACK", False),
        live_venue_mode=get_live_venue_mode(),
    )


def assert_live_entry_allowed(*, testnet: bool, exchange: str) -> LiveCapitalPolicy:
    """Gate non-testnet entries. Returns policy when live submit may proceed."""
    if testnet:
        return load_policy()

    policy = load_policy()
    if not policy.live_trading_enabled:
        raise LiveCapitalError(
            "live_trading_disabled",
            "Live trading disabled (LIVE_TRADING_ENABLED not true)",
        )
    if not policy.phase2_gates_ack:
        raise LiveCapitalError(
            "phase2_gates_incomplete",
            "PHASE2_GATES_ACK not set — Phase-2 release-gates must be acknowledged",
        )
    if policy.nav_quote is None or policy.nav_quote <= 0:
        raise LiveCapitalError(
            "live_nav_required",
            "LIVE_NAV_QUOTE required to enforce ≤5% NAV capital envelope",
        )
    if policy.max_notional is None or policy.max_notional <= 0:
        raise LiveCapitalError(
            "live_cap_invalid",
            "Computed max live notional invalid under ≤5% NAV policy",
        )
    if policy.live_venue_mode != "binance_mainnet":
        raise LiveCapitalError(
            "live_venue_mode_disabled",
            "LIVE_VENUE_MODE must be binance_mainnet for live submit "
            f"(exchange={exchange!r})",
        )
    if exchange.strip().lower() != "binance":
        raise LiveCapitalError(
            "live_venue_unsupported",
            f"Live venue adapter only supports binance (got {exchange!r})",
        )
    return policy


def assert_notional_within_cap(*, notional: float, policy: LiveCapitalPolicy) -> None:
    if policy.max_notional is None:
        raise LiveCapitalError("live_cap_invalid", "max_notional not configured")
    if notional <= 0:
        raise LiveCapitalError(
            "live_notional_invalid",
            "Estimated live notional must be positive",
        )
    if notional > policy.max_notional + 1e-9:
        raise LiveCapitalError(
            "live_notional_exceeds_cap",
            f"Estimated notional {notional} exceeds max_notional "
            f"{policy.max_notional} (≤{policy.max_nav_pct}% of NAV "
            f"{policy.nav_quote})",
        )


def clamp_max_nav_pct(value: float) -> float:
    if value <= 0:
        return DEFAULT_MAX_NAV_PCT
    return min(float(value), 5.0)
