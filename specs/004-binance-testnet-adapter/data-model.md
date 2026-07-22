# Data Model: Binance Testnet Adapter

## VenueMode

| Value | Behavior |
|---|---|
| `internal` | Existing paper matcher (default) |
| `binance_testnet` | Signed Spot Testnet order |

## BinanceOrderRequest (internal)

| Field | Notes |
|---|---|
| symbol | e.g. BTCUSDT |
| side | BUY/SELL |
| type | MARKET |
| quantity | string/decimal per Binance |
| newClientOrderId | from trace_id (safe prefix) |
| timestamp | ms |
| signature | HMAC-SHA256 |

## Ledger mapping

Venue response → `ledger.record_order` (`venue_order_id`=orderId) → fills from `fills[]` or executedQty/price → position/trade as today.
