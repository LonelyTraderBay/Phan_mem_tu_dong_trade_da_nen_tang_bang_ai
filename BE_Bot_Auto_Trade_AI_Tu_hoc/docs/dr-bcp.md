# DR / BCP (condensed)

Full: blueprint **Phần 14**.

## RPO / RTO tiers

| Tier | Data | RPO | RTO |
|---|---|---|---|
| T0 | Vault config (not raw secrets outside Vault) | ≤0 (HA) | ≤15m |
| T1 | Orders, trades, positions, risk_checks, ledger | ≤1m | ≤15m |
| T2 | Kafka audit/order/risk topics | ≤5m | ≤30m |
| T3 | Market data hot | ≤15m | ≤1h |
| T4 | Non-audit metrics/logs | ≤1h | ≤4h |

## Drills

| Drill | Cadence | Pass |
|---|---|---|
| Backup verify | Weekly | Sample restore OK |
| DR restore (staging) | Quarterly | Meet T1 RPO/RTO |
| Game-day KS + DB loss | Pre Phase 2 live + yearly | L3 ≤30s; DB failover in RTO |
| MetaApi outage | 6 months | Correct L1 scope; no blind orders |

## BCP trading stance

During DR: **fail-closed on new entries**; protect open positions with native stops. Mass L3 flatten only with Risk Officer / SRE confirmation.
