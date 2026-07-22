# UX rules

## Always visible

Kill-switch L1–L4 control on every authenticated layout (not buried in a menu).

## Confirmations

| Action | UX |
|---|---|
| L1 / L2 activate | Confirm scope + reason |
| L3 / L4 | Modal + step-up (re-auth / OTP) + typed reason; irreversible warning |
| Resume L2+ / L3 / L4 | Route through Approvals when SoD requires second person |
| Promote canary &gt;10% | Diff + dual-control; cannot self-approve |
| Manual order | Confirm; show pending until ACK — never “filled” early |
| Risk limit change | Propose only; show pending until approved |

## Stale

- Explicit “STALE” badge on charts/tables when feed interrupted.  
- Disable entry actions that depend on live prices while stale (backend will fail-closed anyway).

## RBAC

Hide/disable controls the role cannot call; still handle 403 gracefully. Viewer never sees trade/kill mutate buttons.

## Errors

Map `code` from error model to copy; always offer `trace_id` copy for support.
