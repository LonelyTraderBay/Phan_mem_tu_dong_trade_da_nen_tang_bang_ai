"""Paper venue adapter — internal matcher (default) or Binance Spot Testnet."""

from __future__ import annotations

import os
from typing import Any

from gateway import account_store
from gateway.trading import binance_mainnet, binance_testnet, ledger
from gateway.trading.binance_mainnet import BinanceMainnetClient, BinanceMainnetError
from gateway.trading.binance_testnet import BinanceTestnetClient, BinanceTestnetError
from gateway.trading.live_capital import (
    LiveCapitalError,
    assert_live_entry_allowed,
    assert_notional_within_cap,
)
from gateway.ws_hub import publish_sync

DEFAULT_FILL_PRICE = 100.0
DEFAULT_INTERVAL = "1m"


class VenueAdapterError(Exception):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)


def get_venue_mode() -> str:
    mode = os.environ.get("PAPER_VENUE_MODE", "internal").strip().lower()
    if mode not in ("internal", "binance_testnet"):
        return "internal"
    return mode


def resolve_fill_price(symbol: str, interval: str = DEFAULT_INTERVAL) -> float:
    from gateway import market_store

    candles = market_store.list_candles(symbol=symbol, interval=interval, limit=1)
    if candles:
        return float(candles[-1]["close"])
    return DEFAULT_FILL_PRICE


def submit_and_fill(
    *,
    account_id: str,
    symbol: str,
    side: str,
    quantity: float,
    risk_check_id: str,
    trace_id: str,
    strategy_id: str | None = None,
    interval: str = DEFAULT_INTERVAL,
) -> dict[str, Any]:
    account = account_store.get_account(account_id)
    if account is not None and not account.testnet:
        return _submit_binance_mainnet(
            account_id=account_id,
            symbol=symbol,
            side=side,
            quantity=quantity,
            risk_check_id=risk_check_id,
            trace_id=trace_id,
            strategy_id=strategy_id,
            interval=interval,
        )

    mode = get_venue_mode()
    if mode == "binance_testnet":
        return _submit_binance_testnet(
            account_id=account_id,
            symbol=symbol,
            side=side,
            quantity=quantity,
            risk_check_id=risk_check_id,
            trace_id=trace_id,
            strategy_id=strategy_id,
        )
    return _submit_internal(
        account_id=account_id,
        symbol=symbol,
        side=side,
        quantity=quantity,
        risk_check_id=risk_check_id,
        trace_id=trace_id,
        strategy_id=strategy_id,
        interval=interval,
    )


def _submit_internal(
    *,
    account_id: str,
    symbol: str,
    side: str,
    quantity: float,
    risk_check_id: str,
    trace_id: str,
    strategy_id: str | None,
    interval: str,
) -> dict[str, Any]:
    """Accept order, fill immediately at paper price, update ledger."""
    price = resolve_fill_price(symbol, interval=interval)
    order = ledger.record_order(
        account_id=account_id,
        symbol=symbol,
        side=side,
        quantity=quantity,
        status="filled",
        risk_check_id=risk_check_id,
        trace_id=trace_id,
        strategy_id=strategy_id,
        venue_order_id=f"paper-{trace_id[:8]}",
        price=price,
    )
    ledger.record_fill(
        order_id=order["id"],
        account_id=account_id,
        symbol=symbol,
        side=side,
        quantity=quantity,
        price=price,
        trace_id=trace_id,
        strategy_id=strategy_id,
    )
    position = ledger.upsert_position_from_fill(
        account_id=account_id,
        symbol=symbol,
        side=side,
        quantity=quantity,
        price=price,
        strategy_id=strategy_id,
    )
    trade = ledger.record_trade(
        account_id=account_id,
        symbol=symbol,
        side=side,
        quantity=quantity,
        price=price,
        strategy_id=strategy_id,
    )
    _publish_trading_updates(
        order=order,
        position=position,
        account_id=account_id,
        symbol=symbol,
        side=side,
        quantity=quantity,
        price=price,
        risk_check_id=risk_check_id,
        trace_id=trace_id,
    )
    return {
        "order": order,
        "position": position,
        "trade": trade,
        "fill_price": price,
        "venue": "internal",
    }


def _submit_binance_mainnet(
    *,
    account_id: str,
    symbol: str,
    side: str,
    quantity: float,
    risk_check_id: str,
    trace_id: str,
    strategy_id: str | None,
    interval: str,
) -> dict[str, Any]:
    account = account_store.get_account(account_id)
    if account is None:
        raise VenueAdapterError("not_found", "Account not found for live venue submit")
    try:
        policy = assert_live_entry_allowed(
            testnet=False,
            exchange=account.exchange,
        )
        est_price = resolve_fill_price(symbol, interval=interval)
        assert_notional_within_cap(
            notional=float(quantity) * float(est_price),
            policy=policy,
        )
    except LiveCapitalError as exc:
        raise VenueAdapterError(exc.code, exc.message) from exc

    if not account.credentials:
        raise VenueAdapterError(
            "credentials_required",
            "No API credentials for Binance mainnet submit",
        )

    cred = account.credentials[0]
    try:
        client = BinanceMainnetClient(
            api_key=cred.api_key,
            api_secret=cred.api_secret,
            transport=binance_mainnet.get_test_transport(),
        )
        payload = client.place_market_order(
            symbol=symbol,
            side=side,
            quantity=quantity,
            trace_id=trace_id,
        )
    except BinanceMainnetError as exc:
        raise VenueAdapterError(exc.code, exc.message) from exc

    fill_qty, fill_price = _extract_fill(payload, fallback_qty=quantity)
    try:
        assert_notional_within_cap(
            notional=float(fill_qty) * float(fill_price),
            policy=policy,
        )
    except LiveCapitalError as exc:
        raise VenueAdapterError(exc.code, exc.message) from exc

    venue_order_id = str(payload.get("orderId") or payload.get("clientOrderId") or "")
    status = str(payload.get("status") or "filled").lower()
    if status in ("new", "partially_filled") and fill_qty <= 0:
        raise VenueAdapterError(
            "venue_reject",
            "Binance mainnet order accepted but not filled",
        )

    order = ledger.record_order(
        account_id=account_id,
        symbol=symbol,
        side=side,
        quantity=fill_qty,
        status="filled",
        risk_check_id=risk_check_id,
        trace_id=trace_id,
        strategy_id=strategy_id,
        venue_order_id=venue_order_id or f"bn-m-{trace_id[:8]}",
        price=fill_price,
    )
    ledger.record_fill(
        order_id=order["id"],
        account_id=account_id,
        symbol=symbol,
        side=side,
        quantity=fill_qty,
        price=fill_price,
        trace_id=trace_id,
        strategy_id=strategy_id,
    )
    position = ledger.upsert_position_from_fill(
        account_id=account_id,
        symbol=symbol,
        side=side,
        quantity=fill_qty,
        price=fill_price,
        strategy_id=strategy_id,
    )
    trade = ledger.record_trade(
        account_id=account_id,
        symbol=symbol,
        side=side,
        quantity=fill_qty,
        price=fill_price,
        strategy_id=strategy_id,
    )
    _publish_trading_updates(
        order=order,
        position=position,
        account_id=account_id,
        symbol=symbol,
        side=side,
        quantity=fill_qty,
        price=fill_price,
        risk_check_id=risk_check_id,
        trace_id=trace_id,
    )
    return {
        "order": order,
        "position": position,
        "trade": trade,
        "fill_price": fill_price,
        "venue": "binance_mainnet",
    }


def _submit_binance_testnet(
    *,
    account_id: str,
    symbol: str,
    side: str,
    quantity: float,
    risk_check_id: str,
    trace_id: str,
    strategy_id: str | None,
) -> dict[str, Any]:
    account = account_store.get_account(account_id)
    if account is None:
        raise VenueAdapterError("not_found", "Account not found for venue submit")
    if account.exchange.lower() != "binance":
        raise VenueAdapterError(
            "venue_mismatch",
            "binance_testnet mode requires account.exchange=binance",
        )
    if not account.testnet:
        try:
            assert_live_entry_allowed(testnet=False, exchange=account.exchange)
        except LiveCapitalError as exc:
            raise VenueAdapterError(exc.code, exc.message) from exc
        raise VenueAdapterError(
            "venue_mismatch",
            "binance_testnet mode requires account.testnet=true (refuse live)",
        )
    if not account.credentials:
        raise VenueAdapterError(
            "credentials_required",
            "No API credentials for Binance testnet submit",
        )

    cred = account.credentials[0]
    try:
        client = BinanceTestnetClient(
            api_key=cred.api_key,
            api_secret=cred.api_secret,
            transport=binance_testnet.get_test_transport(),
        )
        payload = client.place_market_order(
            symbol=symbol,
            side=side,
            quantity=quantity,
            trace_id=trace_id,
        )
    except BinanceTestnetError as exc:
        raise VenueAdapterError(exc.code, exc.message) from exc

    fill_qty, fill_price = _extract_fill(payload, fallback_qty=quantity)
    venue_order_id = str(payload.get("orderId") or payload.get("clientOrderId") or "")
    status = str(payload.get("status") or "filled").lower()
    if status in ("new", "partially_filled"):
        # Still record what executed; if zero executed, fail-closed.
        if fill_qty <= 0:
            raise VenueAdapterError(
                "venue_reject",
                "Binance testnet order accepted but not filled",
            )

    order = ledger.record_order(
        account_id=account_id,
        symbol=symbol,
        side=side,
        quantity=fill_qty,
        status="filled",
        risk_check_id=risk_check_id,
        trace_id=trace_id,
        strategy_id=strategy_id,
        venue_order_id=venue_order_id or f"bn-{trace_id[:8]}",
        price=fill_price,
    )
    ledger.record_fill(
        order_id=order["id"],
        account_id=account_id,
        symbol=symbol,
        side=side,
        quantity=fill_qty,
        price=fill_price,
        trace_id=trace_id,
        strategy_id=strategy_id,
    )
    position = ledger.upsert_position_from_fill(
        account_id=account_id,
        symbol=symbol,
        side=side,
        quantity=fill_qty,
        price=fill_price,
        strategy_id=strategy_id,
    )
    trade = ledger.record_trade(
        account_id=account_id,
        symbol=symbol,
        side=side,
        quantity=fill_qty,
        price=fill_price,
        strategy_id=strategy_id,
    )
    _publish_trading_updates(
        order=order,
        position=position,
        account_id=account_id,
        symbol=symbol,
        side=side,
        quantity=fill_qty,
        price=fill_price,
        risk_check_id=risk_check_id,
        trace_id=trace_id,
    )
    return {
        "order": order,
        "position": position,
        "trade": trade,
        "fill_price": fill_price,
        "venue": "binance_testnet",
    }


def _publish_trading_updates(
    *,
    order: dict[str, Any],
    position: dict[str, Any],
    account_id: str,
    symbol: str,
    side: str,
    quantity: float,
    price: float,
    risk_check_id: str,
    trace_id: str,
) -> None:
    publish_sync(
        "trading.orders",
        "orders.update",
        {
            "order_id": order.get("id"),
            "venue_order_id": order.get("venue_order_id"),
            "account_id": account_id,
            "symbol": symbol,
            "side": side,
            "status": order.get("status"),
            "quantity": quantity,
            "price": price,
            "risk_check_id": risk_check_id,
            "timestamp_utc": order.get("updated_at") or order.get("created_at"),
        },
        trace_id=trace_id,
    )
    publish_sync(
        "trading.positions",
        "positions.update",
        {
            "account_id": account_id,
            "symbol": symbol,
            "side": position.get("side"),
            "quantity": position.get("quantity"),
            "entry_price": position.get("entry_price"),
            "mark_price": position.get("mark_price"),
        },
        trace_id=trace_id,
    )


def _extract_fill(payload: dict[str, Any], *, fallback_qty: float) -> tuple[float, float]:
    fills = payload.get("fills")
    if isinstance(fills, list) and fills:
        total_qty = 0.0
        notional = 0.0
        for row in fills:
            if not isinstance(row, dict):
                continue
            q = float(row.get("qty") or row.get("quantity") or 0)
            p = float(row.get("price") or 0)
            total_qty += q
            notional += q * p
        if total_qty > 0:
            return total_qty, notional / total_qty

    executed = float(payload.get("executedQty") or 0)
    if executed > 0:
        # Prefer cummulative quote / qty when present.
        quote = payload.get("cummulativeQuoteQty")
        if quote is not None and float(quote) > 0:
            return executed, float(quote) / executed
        price = payload.get("price")
        if price is not None and float(price) > 0:
            return executed, float(price)

    raise VenueAdapterError(
        "venue_reject",
        "Binance response missing fill quantity/price",
    )
