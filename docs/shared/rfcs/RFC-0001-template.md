# RFC-XXXX: &lt;short title&gt;

| | |
|---|---|
| **Status** | Draft / Approved / Rejected / Superseded |
| **Author** | |
| **Date** | YYYY-MM-DD |
| **Approver (Owner)** | |

## Summary

One paragraph: what changes and why.

## Motivation

Problem / gap. Link related blueprint section or incident.

## Contract diff

- `packages/contracts/VERSION`: current → proposed  
- OpenAPI paths / schemas touched  
- Event subjects / JSON Schema  
- WS channels  
- RBAC / SoD matrix  

Attach before/after snippets or link a PR to `packages/contracts`.

## Phase

Which environment / phase may consume this (1–4). Any gate impact?

## Change class

- [ ] **Additive public** (path/field/event mới) — vẫn cần Owner approve trước khi BE/FE code  
- [ ] **Breaking** — major bump + dual-publish / deprecation window  
- [ ] **Docs-only** (không đổi wire contract)

## Breaking?

- [ ] No (additive, same major)  
- [ ] Yes → major bump + dual-publish / deprecation window

## Alternatives

Options considered and why rejected.

## Approval

| Role | Sign-off | Date |
|---|---|---|
| Owner | | |
| Risk Officer (if limits / kill-switch / capital) | | |
| SRE (if ops / DR) | | |
| Security (if auth / secrets) | | |

**Implement only after Owner approval and contracts updated.**
