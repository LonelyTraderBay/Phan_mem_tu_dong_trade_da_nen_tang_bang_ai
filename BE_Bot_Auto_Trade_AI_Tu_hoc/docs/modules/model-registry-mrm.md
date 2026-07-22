# Model Registry & MRM

**Blueprint:** Phần 03 Registry; Phần 05 MRM.

## Responsibility

Immutable model versions + lineage, metrics, Model Card, states (champion/challenger/shadow/canary/retired). Enforce human gates and dual-control on promote &gt;10% NAV. Support rollback &lt;5 minutes (NFR-03).

## Phase

AI Service Phase 2+; hard MRM gates Phase 3.

## Interfaces

- In: Training artifacts  
- Out: Inference loads; events `model.promoted` / `.rolled_back` / `.retired`  
- Approvals API for promote

## Fail-closed notes

No Model Card → block shadow. Registry down → Inference fail-closed. Bypass SoD on promote → reject + SEV1 audit.
