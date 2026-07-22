# Research: Binance Testnet Adapter

## Decisions

### D1 — Venue: Binance Spot Test Network

- **Decision**: Base `https://testnet.binance.vision` · `POST /api/v3/order` signed HMAC-SHA256 · MARKET orders for activate baseline.
- **Rationale**: Owner named Binance testnet; Spot Test Network is isolated from mainnet.
- **Reject**: Futures testnet URLs; mainnet `api.binance.com`.

### D2 — Mode switch env `PAPER_VENUE_MODE`

- **Decision**: `internal` (default) | `binance_testnet`.
- **Rationale**: Preserve CI with fake credentials; opt-in for real/mocked external venue.

### D3 — No silent fallback

- **Decision**: In `binance_testnet` mode, venue errors → fail activate; do not call internal matcher.
- **Rationale**: Fail-closed; avoids fake fills labeled as testnet.

### D4 — Host allowlist

- **Decision**: Allow only hostnames ending with `testnet.binance.vision` (and exact default). Reject others.
- **Rationale**: Prevent misconfig to live capital API.

### D5 — Public contracts

- **Decision**: No OpenAPI change required (internal adapter). Document in feature contracts/README.
- **Rationale**: Still no public create-order (002 lock).
