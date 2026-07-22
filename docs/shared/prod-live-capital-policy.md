# Prod-live capital policy (≤5% NAV)

**Assignment:** `PROD-LIVE`  
**Owner activation (2026-07-23):** `Active PROD-LIVE — scope: ≤5% NAV …`  
**Ellipsis:** NAV tuyệt đối, Risk Officer chữ ký, venue live adapter — **chưa đủ** → hệ thống **fail-closed**, không gửi mainnet.

## Envelope

| Rule | Value |
|---|---|
| Max live capital | **≤ 5% NAV** (hard ceiling; env không được vượt) |
| Default `LIVE_MAX_NAV_PCT` | `5` |
| Owner NAV (013) | `LIVE_NAV_QUOTE=100000` → max notional **5000** |
| Require `PHASE2_GATES_ACK=true` | Yes |
| Require `LIVE_TRADING_ENABLED=true` | Yes — explicit enable |
| Require `LIVE_VENUE_MODE=binance_mainnet` | Yes — for mainnet submit |
| Mainnet adapter | `binance_mainnet.py` — host `api.binance.com` only |

## Env (see `.env.example`)

```text
LIVE_MAX_NAV_PCT=5
LIVE_NAV_QUOTE=100000            # Owner 2026-07-23 — not committed secrets
LIVE_TRADING_ENABLED=false       # default off — flip only on dedicated host
PHASE2_GATES_ACK=false
LIVE_VENUE_MODE=off              # binance_mainnet when ready
# BINANCE_MAINNET_BASE_URL=https://api.binance.com
```

Keys: `POST /v1/accounts/{id}/api-keys` on `testnet=false` account — **never commit**.

**Cấm:** commit live API keys; bật live trên CI; vượt 5% NAV.
