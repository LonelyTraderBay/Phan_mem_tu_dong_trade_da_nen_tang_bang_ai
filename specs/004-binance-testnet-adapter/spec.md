# Feature Specification: Binance Testnet Adapter

**Feature Branch**: `004-binance-testnet-adapter`

**Created**: 2026-07-22

**Status**: Implemented

**Input**: Owner: `Active PAPER-TESTNET-ADAPTER — venue: Binance testnet` — external crypto paper adapter for Binance Spot Test Network; keep Strategy→Risk→OMS; fail-closed; no live capital; no Deferred.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Paper entry reaches Binance Spot Testnet (Priority: P1)

As a solo paper operator with a Binance **testnet** account and masked API credentials, when venue mode is `binance_testnet` and I activate a simple strategy, the OMS submits a signed testnet order (not mainnet) and the ledger updates from the venue fill response.

**Why this priority**: Replaces internal-only matcher as the next prod-paper hardening step named by Owner.

**Independent Test**: With MockTransport or live testnet keys (local only), activate path produces a venue order id and ledger fill; secrets never appear in logs/responses.

**Acceptance Scenarios**:

1. **Given** `PAPER_VENUE_MODE=binance_testnet`, account `exchange=binance` + `testnet=true` + credentials, **When** strategy activates and risk allows, **Then** adapter calls `https://testnet.binance.vision` (or allowed testnet host) and records fill/position from response.
2. **Given** venue mode is `binance_testnet` but HTTP/API fails, **When** activate runs, **Then** entry fails closed (no invented internal fill).
3. **Given** default `PAPER_VENUE_MODE=internal`, **When** existing paper E2E tests run, **Then** internal matcher behavior is unchanged (CI green without network).

---

### User Story 2 - Refuse live / wrong venue (Priority: P1)

As the system, I must never send orders to Binance **mainnet** from this feature, and must reject non-testnet account configuration when mode is binance_testnet.

**Why this priority**: Capital safety — Owner named testnet only.

**Independent Test**: Base URL validation rejects `api.binance.com`; account with `testnet=false` is rejected in binance_testnet mode.

**Acceptance Scenarios**:

1. **Given** configured base URL is mainnet, **When** adapter initializes/submits, **Then** it refuses (fail-closed).
2. **Given** account `testnet=false` or exchange ≠ binance, **When** mode is binance_testnet, **Then** submit is rejected with a clear non-secret error code.

---

### User Story 3 - Operator wiring docs (Priority: P2)

As Owner/operator, I can configure testnet keys via env / account API keys (already masked) and read a short quickstart without committing secrets.

**Why this priority**: Enables real testnet drills after CI mock path.

**Independent Test**: `.env.example` documents `PAPER_VENUE_MODE` + optional base URL; no real keys in repo.

**Acceptance Scenarios**:

1. **Given** docs/quickstart, **When** operator follows steps, **Then** they know how to set mode + keys without pasting secrets into git.

---

### Edge Cases

- Missing credentials → credentials_required / adapter reject (existing fail-closed).
- Partial fill → record executed qty/price from response; no double-count.
- Timeout / network error → fail-closed, alert optional `VENUE_ERROR`.
- Kill-switch engaged → risk still blocks before adapter (unchanged).

## Requirements *(mandatory)*

### Constitution Constraints *(trading platform)*

Contract-first public shapes unchanged (no public create-order). Secrets never in logs/git. BE-only product code for this assignment. Paper/testnet only — not prod-live.

### Functional Requirements

- **FR-001**: System MUST support `PAPER_VENUE_MODE` = `internal` | `binance_testnet` (default `internal`).
- **FR-002**: In `binance_testnet` mode, adapter MUST call only allowed Binance Spot **testnet** hosts (default `https://testnet.binance.vision`).
- **FR-003**: Adapter MUST refuse mainnet hosts and non-testnet accounts in binance_testnet mode.
- **FR-004**: Orders MUST still require prior risk allow + `risk_check_id` via OMS (unchanged path).
- **FR-005**: Credentials MUST come from account store (server-side); never logged or returned.
- **FR-006**: Venue HTTP client MUST be injectable for pytest (MockTransport); CI MUST NOT require real keys.
- **FR-007**: On venue failure, system MUST NOT fall back to inventing an internal fill while mode is `binance_testnet`.
- **FR-008**: MUST NOT implement live capital, MT5, AI promote, or multi-user SaaS.

### Key Entities

- **VenueMode**: internal | binance_testnet
- **BinanceTestnetOrder**: signed request + venue response mapped to ledger order/fill
- **VenueCredentials**: api_key / api_secret from StoredCredential (server-only)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: pytest covers mock Binance fill path + mainnet URL reject + non-testnet account reject.
- **SC-002**: Existing paper E2E tests remain green with default internal mode.
- **SC-003**: `validate_governance` PASS; no secrets committed.
- **SC-004**: Quickstart documents Owner local live-testnet drill (optional).
