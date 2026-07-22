# Quickstart

Default: live disabled. Testnet accounts unchanged.

To probe envelope (still no mainnet orders):

```text
LIVE_TRADING_ENABLED=true
PHASE2_GATES_ACK=true
LIVE_NAV_QUOTE=100000
LIVE_MAX_NAV_PCT=5
```

Activate strategy on `testnet=false` account → expect `live_venue_not_implemented`.
