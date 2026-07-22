# Implementation Plan: Binance Testnet Adapter

**Branch**: `004-binance-testnet-adapter` (spec) | **Date**: 2026-07-22 | **Spec**: [spec.md](./spec.md)

## Summary

Add a **Binance Spot Testnet** venue adapter behind OMS, selected by `PAPER_VENUE_MODE=binance_testnet`. Default remains internal matcher for CI. Hard-refuse mainnet hosts. Credentials from account store; httpx + injectable transport; fail-closed on venue errors.

## Technical Context

**Language/Version**: Python 3.12 · **Deps**: FastAPI Gateway, httpx  
**Storage**: Existing in-memory account credentials + ledger  
**Testing**: pytest + httpx.MockTransport  
**Constraints**: BE-only; no public create-order; testnet host allowlist only  
**Scale/Scope**: Solo paper, spot MARKET orders on activate path

## Constitution Check

- [x] I Contract-First — no new public order API; reuse accounts/credentials
- [x] II Capital Safety — risk_check_id required; fail-closed; testnet-only host
- [x] III Traceability — trace_id on path; no secret logs
- [x] IV Tests — mock venue + reject mainnet + preserve internal CI
- [x] V Phase — paper testnet only
- [x] Ownership — `BE_Bot_Auto_Trade_AI_Tu_Hoc/` (+ specs/docs/contracts if docs-only)

## Project Structure

```text
specs/004-binance-testnet-adapter/
BE_Bot_Auto_Trade_AI_Tu_Hoc/services/gateway/src/gateway/trading/
  binance_testnet.py
  paper_adapter.py  # dispatch
```

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected |
|---|---|---|
| None | — | — |
