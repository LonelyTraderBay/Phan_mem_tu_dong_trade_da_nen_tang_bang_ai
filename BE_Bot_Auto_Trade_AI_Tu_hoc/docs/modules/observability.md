# Observability Stack

**Blueprint:** Phần 03 Observability; Phần 11; NFR-02.

## Responsibility

Logs (Loki/ELK), metrics (Prometheus/Grafana), OTel traces on Gateway→Strategy→Risk→OMS→Adapter with baggage `trace_id`, `client_order_id`, `signal_id`, `account_id`. WORM audit sink for trade decisions + dual-control.

## Phase

From Phase 1 in parallel — do not defer.

## Interfaces

- In: OTel exporters from services  
- Out: dashboards, alerts, audit archive (object lock)  
- Coverage gate ≥95% hot path by Phase 3 exit

## Fail-closed notes

Missing observability is a release-gate failure for trading changes (DoD Phần 15), not a runtime open of risk checks.
