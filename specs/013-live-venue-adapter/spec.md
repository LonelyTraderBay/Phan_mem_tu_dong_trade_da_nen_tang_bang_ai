# Feature Spec: LIVE-VENUE-ADAPTER

## Overview

Owner activated `LIVE-VENUE-ADAPTER` — Binance **mainnet** Spot, ≤5% NAV, `LIVE_NAV_QUOTE=100000`, Phase-2 Pass recorded, contract-first.

## Requirements

- FR-001: Mainnet REST client allowlists `api.binance.com` only (reject testnet hosts).
- FR-002: Live submit requires `LIVE_TRADING_ENABLED`, `PHASE2_GATES_ACK`, `LIVE_NAV_QUOTE`, `LIVE_VENUE_MODE=binance_mainnet`.
- FR-003: Reject order if estimated notional &gt; 5% of NAV (5000 when NAV=100000).
- FR-004: Secrets via account API keys only — never commit; never log.
- FR-005: Default `LIVE_TRADING_ENABLED=false` / venue mode off in examples.

## Out of scope

- Futures/margin, MT5, Deferred matrix items, committing real keys.
