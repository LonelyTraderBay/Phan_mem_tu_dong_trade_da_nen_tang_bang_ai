# OMS (Order Execution)

**Blueprint:** Phần 03 OMS; Phần 03C state machine.

## Responsibility

Place/cancel via Adapter with idempotency; full order FSM including **UNKNOWN** (must poll status — never blind retry); partial fills; drive reconciliation with Ledger.

## Phase

Core Trading Phase 1.

## Interfaces

- In: Risk-approved intents (`risk_check_id` mandatory)  
- Out: Adapter; events `order.*`  
- Links: `client_order_id`, `trace_id`, `signal_id`

## Fail-closed notes

Missing `risk_check_id` → refuse submit. UNKNOWN → query before any resubmit. Recon break → L2 on scope (Phần 03C).
