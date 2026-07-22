# Tasks: Binance Testnet Adapter

**Assignment**: `PAPER-TESTNET-ADAPTER` (Owner-named, venue=Binance testnet)

## Phase 1 — Setup

- [x] T001 Feature artifacts + `feature.json` + assignment active
- [x] T002 [P] Document env in root `.env.example`

## Phase 2 — Foundational

- [x] T003 BE: `binance_testnet` client (sign, host allowlist, injectable httpx)
- [x] T004 BE: `paper_adapter` dispatch by `PAPER_VENUE_MODE`
- [x] T005 Fail-closed: mainnet host / non-testnet account / HTTP error (no internal fallback)

## Phase 3 — US1 Order path

- [x] T006 [US1] Map venue fill → ledger (order/fill/position/trade)
- [x] T007 [US1] Wire credentials from account_store (no secret logs)
- [x] T008 [US1] pytest MockTransport happy path

## Phase 4 — US2 Safety

- [x] T009 [US2] pytest reject mainnet base URL
- [x] T010 [US2] pytest reject testnet=false account in binance mode
- [x] T011 [US2] Default internal mode: existing E2E still green

## Phase 5 — Close

- [x] T012 Quickstart + HANDOFF note (BE)
- [x] T013 pytest **68 passed** + validate_governance PASS
- [x] T014 assignment → done; spec Status Implemented
