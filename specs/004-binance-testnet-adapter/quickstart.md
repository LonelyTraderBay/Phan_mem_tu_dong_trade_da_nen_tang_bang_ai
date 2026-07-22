# Quickstart: Binance Testnet Adapter

## CI / default

Leave unset or:

```text
PAPER_VENUE_MODE=internal
```

Existing Gateway pytest must pass without network.

## Local Binance Spot Testnet (optional)

1. Create keys at https://testnet.binance.vision (never commit).
2. Set:

```text
PAPER_VENUE_MODE=binance_testnet
# optional override (must remain testnet host):
# BINANCE_TESTNET_BASE_URL=https://testnet.binance.vision
```

3. Login → create account `exchange=binance`, `testnet=true` → register API key/secret via API (masked response).
4. Create/activate strategy → risk allow → signed testnet MARKET order → ledger updates.
5. On API error → activate fails (no fake fill).

## Verify mock path

```text
cd BE_Bot_Auto_Trade_AI_Tu_Hoc/services/gateway
python -m pytest tests/test_binance_testnet_adapter.py -q
```
