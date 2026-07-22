/**
 * Known Gateway operations from packages/contracts/openapi/openapi.yaml.
 * Do not add paths that are absent from that contract.
 */

export type HttpMethod = "GET" | "POST" | "PATCH" | "PUT" | "DELETE";

export type ApiOperation = {
  method: HttpMethod;
  /** OpenAPI path template, e.g. /v1/accounts/{account_id}/api-keys */
  path: string;
};

/**
 * operationId → method + path (OpenAPI 0.1.0 stubs).
 * Paths with `{param}` require `pathParams` when calling the client.
 */
export const API_OPERATIONS = {
  getHealth: { method: "GET", path: "/health" },
  getReady: { method: "GET", path: "/ready" },
  postAuthLogin: { method: "POST", path: "/v1/auth/login" },
  postAuthRefresh: { method: "POST", path: "/v1/auth/refresh" },
  postAuthLogout: { method: "POST", path: "/v1/auth/logout" },
  postAccounts: { method: "POST", path: "/v1/accounts" },
  postAccountApiKeys: {
    method: "POST",
    path: "/v1/accounts/{account_id}/api-keys",
  },
  getStrategies: { method: "GET", path: "/v1/strategies" },
  postStrategies: { method: "POST", path: "/v1/strategies" },
  patchStrategy: { method: "PATCH", path: "/v1/strategies/{strategy_id}" },
  getMarketSymbols: { method: "GET", path: "/v1/market/symbols" },
  getMarketCandles: { method: "GET", path: "/v1/market/candles" },
  getPositions: { method: "GET", path: "/v1/positions" },
  getPnlSummary: { method: "GET", path: "/v1/pnl/summary" },
  getReportsTrades: { method: "GET", path: "/v1/reports/trades" },
  getKillSwitchStatus: { method: "GET", path: "/v1/kill-switch" },
  postKillSwitch: { method: "POST", path: "/v1/kill-switch" },
  getAlerts: { method: "GET", path: "/v1/alerts" },
  /** Deferred (x-mvp: false) — present in contract map only; do not ship as live UI. */
  postModelPromote: {
    method: "POST",
    path: "/v1/models/{model_id}/promote",
  },
} as const satisfies Record<string, ApiOperation>;

export type OperationId = keyof typeof API_OPERATIONS;

export function resolveOperationPath(
  pathTemplate: string,
  pathParams?: Record<string, string>,
): string {
  return pathTemplate.replace(/\{([^}]+)\}/g, (_match, name: string) => {
    const value = pathParams?.[name];
    if (value === undefined || value === "") {
      throw new Error(`Missing path param: ${name}`);
    }
    return encodeURIComponent(value);
  });
}
