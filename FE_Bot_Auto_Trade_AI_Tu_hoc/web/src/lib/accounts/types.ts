/**
 * Account / API-key shapes from packages/contracts/openapi/openapi.yaml.
 * Do not invent fields.
 */

export type MarketType = "spot" | "futures";

export type AccountCreate = {
  name: string;
  exchange: string;
  market_type: MarketType;
  testnet?: boolean;
};

export type AccountStatus = "active" | "disabled" | "error";

export type Account = {
  id: string;
  name: string;
  exchange: string;
  market_type: MarketType;
  testnet: boolean;
  status: AccountStatus;
  created_at: string;
  updated_at?: string;
};

export type ApiKeyCreate = {
  label: string;
  api_key: string;
  api_secret: string;
  passphrase?: string;
};

export type ApiKeyMasked = {
  id: string;
  account_id: string;
  label: string;
  masked_api_key: string;
  created_at: string;
  last_validated_at?: string | null;
};

function isMarketType(value: unknown): value is MarketType {
  return value === "spot" || value === "futures";
}

function isAccountStatus(value: unknown): value is AccountStatus {
  return value === "active" || value === "disabled" || value === "error";
}

export function parseAccount(data: unknown): Account | null {
  if (typeof data !== "object" || data === null) return null;
  const o = data as Record<string, unknown>;
  if (typeof o.id !== "string" || o.id.length === 0) return null;
  if (typeof o.name !== "string") return null;
  if (typeof o.exchange !== "string") return null;
  if (!isMarketType(o.market_type)) return null;
  if (typeof o.testnet !== "boolean") return null;
  if (!isAccountStatus(o.status)) return null;
  if (typeof o.created_at !== "string") return null;

  const account: Account = {
    id: o.id,
    name: o.name,
    exchange: o.exchange,
    market_type: o.market_type,
    testnet: o.testnet,
    status: o.status,
    created_at: o.created_at,
  };
  if (typeof o.updated_at === "string") {
    account.updated_at = o.updated_at;
  }
  return account;
}

export function parseApiKeyMasked(data: unknown): ApiKeyMasked | null {
  if (typeof data !== "object" || data === null) return null;
  const o = data as Record<string, unknown>;
  if (typeof o.id !== "string" || o.id.length === 0) return null;
  if (typeof o.account_id !== "string" || o.account_id.length === 0) return null;
  if (typeof o.label !== "string") return null;
  if (typeof o.masked_api_key !== "string") return null;
  if (typeof o.created_at !== "string") return null;

  const key: ApiKeyMasked = {
    id: o.id,
    account_id: o.account_id,
    label: o.label,
    masked_api_key: o.masked_api_key,
    created_at: o.created_at,
  };
  if (o.last_validated_at === null || typeof o.last_validated_at === "string") {
    key.last_validated_at = o.last_validated_at as string | null;
  }
  return key;
}
