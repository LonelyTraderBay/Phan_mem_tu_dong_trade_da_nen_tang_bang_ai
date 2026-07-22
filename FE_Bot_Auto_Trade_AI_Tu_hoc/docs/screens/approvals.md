# Approvals

**Blueprint:** Phần 04 Approvals; Phần 03D SoD.

## Purpose

Dual-control queue: risk-limit changes, resume L2+, canary promote. Show before/after diff; require approval reason.

## API / WS deps

- REST: list pending, approve, reject  
- WS: queue updates

## UX rules

Hide Approve if current user is proposer. Require typed reason. After decision, reflect audit trail id / trace_id. Never silently auto-approve in UI.
