# Generate TypeScript client from OpenAPI (later)

When `packages/contracts/openapi/openapi.yaml` is stable enough for FE:

## Option A — openapi-typescript + openapi-fetch

```bash
cd FE_Bot_Auto_Trade_AI_Tu_Hoc/web
npx openapi-typescript ../../packages/contracts/openapi/openapi.yaml -o src/lib/api/schema.d.ts
```

## Option B — @hey-api/openapi-ts

```bash
npx @hey-api/openapi-ts \
  -i packages/contracts/openapi/openapi.yaml \
  -o FE_Bot_Auto_Trade_AI_Tu_Hoc/web/src/lib/api/generated
```

## Rules

1. Regenerate after every approved contract RFC that touches OpenAPI.  
2. Do not hand-edit generated files.  
3. Point `NEXT_PUBLIC_API_URL` at Gateway; never hard-code BE service URLs.  
4. Run `scripts/validate-contracts.ps1` (or `.sh`) before generating.
