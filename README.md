# Bot Auto-Trade AI — monorepo

Enterprise auto-trade platform (crypto / forex / equities) with AI retrain loop. **Contract-first**: Backend và Frontend làm song song, khớp tại `packages/contracts`.

## Root layout (2 folder chính)

```
BE_Bot_Auto_Trade_AI_Tu_Hoc/     # Toàn bộ Backend
  services/                      # gateway, core-trading, data, ai, backtest
  infra/                         # compose, vault, k8s
  docs/                          # modules, ADR, HANDOFF-AI
FE_Bot_Auto_Trade_AI_Tu_Hoc/     # Toàn bộ Frontend
  web/                           # Next.js app
  docs/                          # screens, UX, HANDOFF-AI
packages/contracts/              # Shared — OpenAPI, events, RBAC, WS
docs/{architecture,shared,superpowers}/
scripts/
```

## Design & architecture

| Doc | Role |
|---|---|
| [AGENTS.md](AGENTS.md) | Luật thực thi bắt buộc cho mọi AI |
| [agent-assignment.yaml](docs/shared/agent-assignment.yaml) | Assignment máy đọc — chỉ id `active` được Owner gọi |
| [MVP capability matrix](docs/shared/mvp-capability-matrix.md) | In-MVP vs Deferred + lane ownership |
| [Governance CI](.github/workflows/governance.yml) | Ép contracts/matrix/rules trên mọi PR |
| [BE/FE split prep design](docs/superpowers/specs/2026-07-22-be-fe-split-prep-design.md) | Thiết kế tách ownership |
| [Architecture INDEX](docs/architecture/INDEX.md) | Con trỏ tài liệu |
| [Blueprint v2.1](docs/architecture/Kien-truc-Bot-Auto-Trade-AI-v2-Enterprise.md) | Tham chiếu — **không** phải backlog tự code |

## Ownership

| Role | Được sửa | Không được sửa |
|---|---|---|
| **Frontend AI** | `FE_Bot_Auto_Trade_AI_Tu_Hoc/` | `BE_Bot_Auto_Trade_AI_Tu_Hoc/` |
| **Backend AI** | `BE_Bot_Auto_Trade_AI_Tu_Hoc/` | `FE_Bot_Auto_Trade_AI_Tu_Hoc/` |
| **Shared (RFC)** | `packages/contracts`, `docs/shared` | Implement trước khi RFC duyệt |
| **Owner** | Merge RFC, breaking change | — |

Hard rules: FE không import code trong folder BE. BE không commit vào folder FE. Path API/WS/event mới phải vào contracts trước.

Handoffs:
- [BE HANDOFF](BE_Bot_Auto_Trade_AI_Tu_Hoc/docs/HANDOFF-AI.md)
- [FE HANDOFF](FE_Bot_Auto_Trade_AI_Tu_Hoc/docs/HANDOFF-AI.md)

## Validate contracts

```powershell
.\scripts\validate-contracts.ps1
```

```bash
./scripts/validate-contracts.sh
```

## Local compose

```powershell
Copy-Item .env.example .env
docker compose -f BE_Bot_Auto_Trade_AI_Tu_Hoc/infra/compose/docker-compose.yml --env-file .env up -d
```

- Gateway: http://localhost:8000/health  
- Web: http://localhost:3000  
- Vault/k8s: Phase sau (`BE_Bot_Auto_Trade_AI_Tu_Hoc/infra/vault`, `.../k8s`)

## Generate FE client (sau này)

Xem [scripts/generate-fe-client.md](scripts/generate-fe-client.md).
