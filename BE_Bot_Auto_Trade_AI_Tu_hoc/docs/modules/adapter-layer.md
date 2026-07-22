# Exchange / Broker Adapter Layer

**Blueprint:** Phần 03 Adapter; Phần 10.

## Responsibility

Normalize connect / market data / orders / positions / fees / margin behind one interface. One adapter per venue (CCXT crypto, MT5 MetaApi/official/EA, IBKR/Alpaca). Symbol registry + rate-limit budgets live here.

## Phase

Core Trading module Phase 1; split container Phase 3–4 if load requires (ADR-02).

## Interfaces

- Called by: Market Data, OMS  
- Emits: normalized `candle.closed` (via bus)  
- Contract tests per adapter (Phần 15)

## Fail-closed notes

Rate budget exhausted → bounded queue + SEV2, never spam venue. Disconnect → health event; Risk applies L1/L2 per runbook — no blind retries.
