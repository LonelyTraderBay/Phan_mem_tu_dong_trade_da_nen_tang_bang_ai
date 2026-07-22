# Strategy Engine

**Blueprint:** Phần 03 Strategy; ADR-04.

## Responsibility

Combine AI signals with regime/liquidity filters; size positions (≤25% Kelly after fees); call Risk **synchronously** before OMS.

## Phase

Core Trading Phase 1 (rule-based first); AI-driven Phase 2.

## Interfaces

- In: `signal.generated` / config  
- Out: sync RPC to Risk → OMS on approve  
- Never bypass Risk

## Fail-closed notes

Risk timeout/unavailable → block all new orders. Strategy risk params cannot exceed Account/Portfolio ceilings (enforced in Risk).
