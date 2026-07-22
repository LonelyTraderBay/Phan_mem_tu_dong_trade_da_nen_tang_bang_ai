# Dashboard

**Blueprint:** Phần 04 Dashboard.

## Purpose

At-a-glance equity (reporting currency), today/total P&L, running bots, recent SEV alerts, venue connection health, error-budget remaining.

## API / WS deps

- REST: portfolio summary, health, alerts digest  
- WS: equity/positions ticks, alert stream, connection status

## UX rules

Stale banner if portfolio feed lags. No client-side equity invention. SEV1 visually distinct. Link to kill-switch / Approvals when pending SoD items exist.
