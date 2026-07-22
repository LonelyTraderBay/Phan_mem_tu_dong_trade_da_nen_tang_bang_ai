# Strategy Builder

**Blueprint:** Phần 04 Strategy / Bot Builder.

## Purpose

Create/edit strategy config (params, model binding, risk ceilings). Later: drag-drop builder.

## API / WS deps

- REST: strategies CRUD, validation errors  
- WS: optional live status of running bots

## UX rules

Client validation for UX only — Backend enforces account/portfolio risk ceilings. Reject UX that suggests bypassing Risk. Show pending dual-control if limit change proposed.
