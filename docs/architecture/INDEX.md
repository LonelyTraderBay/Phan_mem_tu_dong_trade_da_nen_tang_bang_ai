# Architecture index

Canonical blueprint (do not duplicate here):

- **[Kien-truc-Bot-Auto-Trade-AI-v2-Enterprise.md](./Kien-truc-Bot-Auto-Trade-AI-v2-Enterprise.md)** — Enterprise Architecture Blueprint v2.1

## Split docs (day-to-day)

| Area | Path | Audience |
|---|---|---|
| Shared contracts & gates | [docs/shared/](../shared/README.md) | BE + FE + Owner |
| Backend | [BE_Bot_Auto_Trade_AI_Tu_Hoc/docs/](../../BE_Bot_Auto_Trade_AI_Tu_Hoc/docs/README.md) | Backend AI / SRE |
| Frontend | [FE_Bot_Auto_Trade_AI_Tu_Hoc/docs/](../../FE_Bot_Auto_Trade_AI_Tu_Hoc/docs/README.md) | Frontend AI |
| Machine-readable contracts | [packages/contracts/](../../packages/contracts/) | API/WS/events/RBAC |

## Design prep

- [BE/FE split prep design](../superpowers/specs/2026-07-22-be-fe-split-prep-design.md)

## Reading order

1. Shared: API overview, auth/SoD, error model, release gates  
2. Lane của bạn (`BE_Bot_Auto_Trade_AI_Tu_Hoc/docs` hoặc `FE_Bot_Auto_Trade_AI_Tu_Hoc/docs`)  
3. Blueprint chỉ khi cần ngữ cảnh sâu
