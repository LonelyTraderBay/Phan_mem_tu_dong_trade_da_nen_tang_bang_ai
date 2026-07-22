# Strategy Builder

> **Out of MVP:** No-code / drag-drop builder is **Deferred** — matrix `no-code-builder`
> (phase-4). Phase 1 uses form-based simple strategy only (`simple-strategy-run`).

**Blueprint:** Phần 04 Strategy / Bot Builder.

## Purpose

Create/edit strategy config (params, model binding, risk ceilings). Later: drag-drop builder.

## API / WS deps

- REST: `getStrategies`, `postStrategies`, `patchStrategy` (`x-mvp: true`) for simple forms
- WS: optional live status of running bots

## UX rules

Client validation for UX only — Backend enforces account/portfolio risk ceilings. Reject UX that suggests bypassing Risk. Show pending dual-control if limit change proposed. Do not ship no-code canvas as MVP.
