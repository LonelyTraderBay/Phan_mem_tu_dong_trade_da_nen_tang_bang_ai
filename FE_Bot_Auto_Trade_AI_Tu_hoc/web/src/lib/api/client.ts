import { clearTokens, getAccessToken } from "./auth-storage";
import { ApiError } from "./errors";
import type {
  Account,
  AccountCreate,
  ActionResult,
  Alert,
  AlertSeverity,
  ApiErrorBody,
  ApiKeyCreate,
  ApiKeyMasked,
  Candle,
  CandleInterval,
  KillSwitchRequest,
  KillSwitchStatus,
  LoginRequest,
  LogoutRequest,
  MarketSymbol,
  MarketType,
  PnlSummary,
  Position,
  RefreshTokenRequest,
  Strategy,
  StrategyCreate,
  StrategyPatch,
  StrategyStatus,
  TokenPair,
  TradeReport,
} from "./types";

export type ApiResult<T> = {
  data: T;
  stale: boolean;
  headers: Headers;
};

function apiBaseUrl(): string {
  const base = process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "");
  if (!base) {
    throw new ApiError(0, null, "NEXT_PUBLIC_API_URL is not set");
  }
  return base;
}

function isStaleResponse(headers: Headers): boolean {
  const raw =
    headers.get("X-Data-Stale") ??
    headers.get("x-data-stale") ??
    headers.get("X-Stale");
  if (!raw) return false;
  const v = raw.trim().toLowerCase();
  return v === "1" || v === "true" || v === "yes";
}

async function parseErrorBody(res: Response): Promise<ApiErrorBody | null> {
  try {
    const json = (await res.json()) as Partial<ApiErrorBody>;
    if (
      typeof json?.code === "string" &&
      typeof json?.message === "string" &&
      typeof json?.trace_id === "string"
    ) {
      return json as ApiErrorBody;
    }
    return null;
  } catch {
    return null;
  }
}

type RequestOptions = {
  method?: string;
  body?: unknown;
  query?: Record<string, string | number | boolean | undefined | null>;
  auth?: boolean;
  signal?: AbortSignal;
};

async function request<T>(path: string, options: RequestOptions = {}): Promise<ApiResult<T>> {
  const { method = "GET", body, query, auth = true, signal } = options;
  const url = new URL(path.startsWith("http") ? path : `${apiBaseUrl()}${path}`);
  if (query) {
    for (const [key, value] of Object.entries(query)) {
      if (value === undefined || value === null || value === "") continue;
      url.searchParams.set(key, String(value));
    }
  }

  const headers: Record<string, string> = {
    Accept: "application/json",
  };
  if (body !== undefined) {
    headers["Content-Type"] = "application/json";
  }
  if (auth) {
    const token = getAccessToken();
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }
  }

  let res: Response;
  try {
    res = await fetch(url.toString(), {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
      signal,
      cache: "no-store",
    });
  } catch (err) {
    throw new ApiError(
      0,
      null,
      err instanceof Error ? err.message : "Network request failed",
    );
  }

  if (!res.ok) {
    const errBody = await parseErrorBody(res);
    if (res.status === 401) {
      clearTokens();
    }
    throw new ApiError(res.status, errBody, res.statusText || `HTTP ${res.status}`);
  }

  if (res.status === 204) {
    return { data: undefined as T, stale: isStaleResponse(res.headers), headers: res.headers };
  }

  const data = (await res.json()) as T;
  return { data, stale: isStaleResponse(res.headers), headers: res.headers };
}

/** Typed MVP operations — paths match OpenAPI only. */

export function postAuthLogin(body: LoginRequest) {
  return request<TokenPair>("/v1/auth/login", { method: "POST", body, auth: false });
}

export function postAuthRefresh(body: RefreshTokenRequest) {
  return request<TokenPair>("/v1/auth/refresh", { method: "POST", body, auth: false });
}

export function postAuthLogout(body?: LogoutRequest) {
  return request<ActionResult>("/v1/auth/logout", { method: "POST", body: body ?? {} });
}

export function postAccounts(body: AccountCreate) {
  return request<Account>("/v1/accounts", { method: "POST", body });
}

export function postAccountApiKeys(accountId: string, body: ApiKeyCreate) {
  return request<ApiKeyMasked>(`/v1/accounts/${accountId}/api-keys`, {
    method: "POST",
    body,
  });
}

export function getStrategies(params: {
  account_id: string;
  status?: StrategyStatus;
}) {
  return request<Strategy[]>("/v1/strategies", { query: params });
}

export function postStrategies(body: StrategyCreate) {
  return request<Strategy>("/v1/strategies", { method: "POST", body });
}

export function patchStrategy(strategyId: string, body: StrategyPatch) {
  return request<Strategy>(`/v1/strategies/${strategyId}`, { method: "PATCH", body });
}

export function getMarketSymbols(params?: {
  exchange?: string;
  market_type?: MarketType;
}) {
  return request<MarketSymbol[]>("/v1/market/symbols", { query: params });
}

export function getMarketCandles(params: {
  symbol: string;
  interval: CandleInterval;
  start_time?: string;
  end_time?: string;
  limit?: number;
}) {
  return request<Candle[]>("/v1/market/candles", { query: params });
}

export function getPositions(params: {
  account_id: string;
  symbol?: string;
  open_only?: boolean;
}) {
  return request<Position[]>("/v1/positions", { query: params });
}

export function getPnlSummary(params: {
  account_id: string;
  from?: string;
  to?: string;
}) {
  return request<PnlSummary>("/v1/pnl/summary", { query: params });
}

export function getReportsTrades(params: {
  account_id: string;
  strategy_id?: string;
  from?: string;
  to?: string;
  limit?: number;
}) {
  return request<TradeReport[]>("/v1/reports/trades", { query: params });
}

export function getKillSwitchStatus() {
  return request<KillSwitchStatus>("/v1/kill-switch");
}

export function postKillSwitch(body: KillSwitchRequest) {
  return request<KillSwitchStatus>("/v1/kill-switch", { method: "POST", body });
}

export function getAlerts(params: {
  account_id: string;
  acknowledged?: boolean;
  severity?: AlertSeverity;
  limit?: number;
}) {
  return request<Alert[]>("/v1/alerts", { query: params });
}
