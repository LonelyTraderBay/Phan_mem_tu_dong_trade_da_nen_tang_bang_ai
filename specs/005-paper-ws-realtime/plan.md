# Implementation Plan: Paper WS Realtime

**Date**: 2026-07-22 | **Spec**: [spec.md](./spec.md)

## Summary

Add Gateway WS ticket REST + `/ws` hub with locked paper channels; broadcast from kill-switch / paper fills / alerts; FE ticket client + stale banner. Contracts via RFC-0003 (0.3.0).

## Technical Context

Python FastAPI WebSocket + httpx/pytest TestClient; Next.js FE. In-memory ticket store + connection hub for paper Phase 1.

## Constitution Check

- [x] Contract-first RFC-0003 + OpenAPI `postWsTicket`
- [x] Capital safety unchanged (WS is read/notify; orders still via risk path)
- [x] No secrets in frames
- [x] Tests for ticket/WS; FE tsc
- [x] Paper only; FE Gateway-only
- [x] BE/FE ownership respected

## Structure

```text
BE: gateway/ws_ticket_store.py, ws_hub.py, routers/ws_ticket.py, ws route on app
FE: lib/ws/*, components/WsStatusBar.tsx
contracts: openapi 0.3.0, ws-protocol.md, examples
```
