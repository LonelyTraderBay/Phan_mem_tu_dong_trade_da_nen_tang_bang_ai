# Data contracts

**Do not redefine schemas here.**

| Artifact | Path |
|---|---|
| Semver | `packages/contracts/VERSION` |
| OpenAPI | `packages/contracts/openapi/openapi.yaml` |
| Events | `packages/contracts/events/*.schema.json` |
| RBAC | `packages/contracts/rbac/roles.yaml` |
| WS protocol | `packages/contracts/ws/ws-protocol.md` |

Human overview: [docs/shared/api-overview.md](../shared/api-overview.md), [error-model.md](../shared/error-model.md).

Domain entities & event subjects: blueprint **Phần 03B**. Physical DDL locked in Phase 0; logical tables listed there (`orders`, `trades`, `positions`, `risk_checks`, `audit_events`, …).

Compatibility: `BACKWARD` within major; breaking → major + dual-publish window. CI must fail incompatible schemas.
