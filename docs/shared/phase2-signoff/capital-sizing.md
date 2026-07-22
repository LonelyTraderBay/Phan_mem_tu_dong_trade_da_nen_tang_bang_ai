# Sign-off: Capital sizing (G-05)

**Owner activation:** `PROD-LIVE` scope **≤5% NAV** (2026-07-23).  
Policy code: [prod-live-capital-policy.md](../prod-live-capital-policy.md) · hard ceiling 5%.

| Field | Value |
|---|---|
| NAV reference date / source | Owner to set at live-enable; policy ceiling binding |
| NAV amount (`LIVE_NAV_QUOTE`) | **Required in env before any live order** — not set in git |
| Max live capital | ≤5% NAV (hard ceiling in `live_capital.py`) |
| Enforcement (03D / kill) | `live_capital` guard + kill-switch + `PHASE2_GATES_ACK` |
| Owner acknowledge | ≤5% NAV scope; Phase-2 auto-check complete 2026-07-23 |
| Risk acknowledge | Owner acting Risk |
| Effective date | 2026-07-23 (policy); numeric NAV at adapter enable |
| Result | **Pass** (written ≤5% ceiling; absolute NAV deferred to env at live) |

Live keys **forbidden** until live venue adapter feature exists. Set `LIVE_NAV_QUOTE` + `PHASE2_GATES_ACK` + `LIVE_TRADING_ENABLED` only then.
