# @bot/web

Frontend for the multi-platform AI trading bot.

## Ownership

- **Owns:** toàn bộ `FE_Bot_Auto_Trade_AI_Tu_Hoc/` (`web/`, `docs/`)
- **Consumes:** `packages/contracts`
- **Does not edit:** `BE_Bot_Auto_Trade_AI_Tu_Hoc/`

## Setup

```bash
cp .env.example .env.local
npm install
npm run dev
```

App: [http://localhost:3000](http://localhost:3000).

## Scripts

| Script | Description |
|--------|-------------|
| `dev` | Next.js development server |
| `build` | Production build |
| `start` | Serve production build |
| `lint` | ESLint via Next.js |

## Env

- `NEXT_PUBLIC_API_URL` — REST API base (Gateway)
- `NEXT_PUBLIC_WS_URL` — WebSocket endpoint
