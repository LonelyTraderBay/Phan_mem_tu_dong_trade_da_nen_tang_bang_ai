# Reports & History

**Blueprint:** Phần 04 Reports.

## Purpose

Trade history, CSV export, P&L in reporting currency, weekly/monthly reports, audit export by `trace_id` / `client_order_id`.

## API / WS deps

- REST only (paginated queries, downloads)

## UX rules

Server-side filtering. Display reporting currency per ADR-08. Audit export may require elevated role + step-up — handle 403/step-up flows.
