# Account & API Keys

**Blueprint:** Phần 04 Account & API Key; Phần 10.

## Purpose

Register broker credentials once; thereafter masked; connection status; remind disable withdraw; MT5 master vs investor password distinction.

## API / WS deps

- REST: accounts CRUD, key submit (write-once), connection test  
- WS: optional connection health

## UX rules

Never re-display full secret after save. No secrets in client logs. Step-up if exporting/rotating. Warn on missing withdraw-disable.
