# Alerts

**Blueprint:** Phần 04 Alerts; Phần 11 SEV.

## Purpose

Configure channels/thresholds; inbox for SEV1/2/3; acknowledge SEV1.

## API / WS deps

- REST: alert rules, history  
- WS: realtime alert push

## UX rules

SEV1 requires explicit ack UX. Do not bury page-worthy alerts. Link to related kill-switch / recon / approval when payload includes refs.
