# Account & API Keys

> **In-MVP:** Mask credentials after save; never re-display full secret. Matrix id
> `broker-credentials` (`postAccounts`, `postAccountApiKeys`).

**Blueprint:** Phần 04 Account & API Key; Phần 10.

## Purpose

Register broker credentials once; thereafter masked; connection status; remind disable withdraw; MT5 master vs investor password distinction (MT5 adapter itself is Deferred for first crypto paper day).

## API / WS deps

- REST: `postAccounts`, `postAccountApiKeys` (`x-mvp: true`); connection test as available
- WS: optional connection health

## UX rules

Never re-display full secret after save. No secrets in client logs. Step-up if exporting/rotating. Warn on missing withdraw-disable. Stub `501` is OK — UI must not claim “connected live” without Backend confirmation.
