# Shared docs

Ownership: **Shared (RFC)**. Both BE and FE consume this layer; neither owns unilateral contract changes.

## Rules

1. **Contracts first** — any new REST path, WS channel, event subject, role, or error code lands in `packages/contracts` *before* implementation.
2. **Breaking change** = major bump in `packages/contracts/VERSION` + RFC under `docs/shared/rfcs/` + Owner approve.
3. FE talks **only** to Gateway (REST + WS). FE never subscribes to the Event Bus.
4. Do not copy 1300-line blueprint text here — link to [architecture INDEX](../architecture/INDEX.md).

## Contents

| Doc | Purpose |
|---|---|
| [mvp-capability-matrix.md](./mvp-capability-matrix.md) | **Phạm vi Phase 1** In-MVP vs Deferred + lane ownership |
| [mvp-capability-matrix.yaml](./mvp-capability-matrix.yaml) | Bản máy của matrix (canonical) |
| [api-overview.md](./api-overview.md) | REST / WS / events split |
| [auth-rbac-sod.md](./auth-rbac-sod.md) | Roles + dual-control |
| [error-model.md](./error-model.md) | Error JSON schema |
| [websocket-protocol.md](./websocket-protocol.md) | WS summary → contracts |
| [environments.md](./environments.md) | dev → prod-live |
| [release-gates.md](./release-gates.md) | Phase checklists |
| [glossary.md](./glossary.md) | Key terms |
| [rfcs/RFC-0001-template.md](./rfcs/RFC-0001-template.md) | RFC template |
