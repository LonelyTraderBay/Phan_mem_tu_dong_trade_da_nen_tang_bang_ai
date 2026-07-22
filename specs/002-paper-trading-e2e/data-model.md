# Data Model: Paper Trading E2E

**Feature**: `002-paper-trading-e2e`

## Entities

### PaperAccount
- id (uuid)
- name, exchange, market_type, testnet
- status (active|disabled|error)
- credential_ref (opaque; never full secret to FE)
- created_at / updated_at

### ApiKeyMetadata
- id, account_id, label
- masked_api_key
- created_at, last_validated_at?

### SimpleStrategy
- id, account_id, name, symbol, timeframe
- status: draft|active|paused|stopped
- max_position_size?, stop_loss_percent?
- created_at / updated_at

### RiskCheck
- risk_check_id
- decision: allow|deny
- reason_code
- trace_id
- created_at

### PaperOrder
- id / client_order_id
- strategy_id?, account_id
- symbol, side, quantity, status
- risk_check_id (required before submit)
- venue_order_id?
- trace_id
- timestamps

### Position / PnlSnapshot / TradeReport
- As already shaped in OpenAPI `Position`, `PnlSummary`, `TradeReport` — server authoritative

### KillSwitchState
- engaged (bool)
- reason?
- updated_at, updated_by?

### Alert
- id, severity, code, message, acknowledged, timestamps
- account_id?

## State machines (paper)

### Strategy status
`draft → active → paused ↔ active → stopped` (stopped terminal for demo; recreate if needed)

### Order (minimal paper)
`pending_risk → rejected_risk | pending_submit → accepted|filled|canceled|unknown`

### Kill-switch L1
`disengaged ↔ engaged` (engaged blocks new entries)

## Integrity rules

1. No PaperOrder submit without RiskCheck allow + risk_check_id.
2. Fail-closed: missing risk dependency ⇒ deny entries.
3. Secrets never appear in ApiKeyMetadata responses or logs.
4. FE must not invent Position/Pnl/Trade rows.
