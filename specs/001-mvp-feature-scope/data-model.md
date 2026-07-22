# Data Model: MVP Feature Scope Optimization

## Entities

### Capability

| Field | Type | Rules |
|---|---|---|
| id | string | Stable slug, e.g. `emergency-pause` |
| name | string | Human title |
| description | string | One short paragraph |
| status | enum | `in_mvp` \| `deferred` |
| rationale | string | Required; one line why |
| lane | enum | `backend` \| `frontend` \| `both` \| `shared` \| `n_a` |
| contract_touch | boolean | True if `packages/contracts` must change first |
| contract_refs | string[] | OpenAPI operationId / event subject / docs-only |
| phase_return | string \| null | Required when deferred, e.g. `phase-3` |
| safety_critical | boolean | True for pause, risk, credentials |

**Validation**:
- Every `in_mvp` row MUST have a non-empty `lane` other than `n_a` (unless
  `shared` docs-only capability).
- Every `deferred` row MUST set `phase_return`.
- If `contract_touch` is true, `contract_refs` MUST be non-empty.

### CapabilityMatrix

| Field | Type | Rules |
|---|---|---|
| version | semver string | e.g. `0.1.0` |
| updated_at | date | ISO date |
| primary_market | enum | `crypto_paper` (MVP default) |
| operator_profile | enum | `solo_paper` |
| capabilities | Capability[] | MUST cover catalog agreed in research/spec |

### LaneAssignment (derived view)

Not stored separately — query `capabilities` where `status=in_mvp` grouped by
`lane`.

## Relationships

- CapabilityMatrix 1—N Capability
- Capability 0—N contract_refs → OpenAPI paths / event subjects in
  `packages/contracts` (logical reference, not FK)

## State transitions

None for runtime. Governance transition only:

`proposed` → `accepted` (owner sign-off on matrix version) → `amended`
(requires rationale + version bump). Amendments that move an item from
`deferred` → `in_mvp` require owner written approval (spec US1/AC3).
