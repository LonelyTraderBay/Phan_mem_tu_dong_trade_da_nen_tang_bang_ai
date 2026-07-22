/**
 * Portfolio API — OpenAPI getPositions / getPnlSummary / getReportsTrades.
 * Returns server fields only; callers must not derive PnL client-side.
 */

import {
  apiCall,
  formatApiFailureForUi,
  toApiFailure,
  type ApiFailure,
  type ApiResult,
} from "@/lib/api/client";
import { getAccessToken } from "@/lib/auth/tokenStore";
import {
  parsePnlSummary,
  parsePositionList,
  parseTradeReportList,
  type PnlSummary,
  type Position,
  type TradeReport,
} from "./types";

function invalidBodyFailure(status: number, message: string) {
  return toApiFailure({
    status,
    body: {
      code: "INVALID_RESPONSE",
      message,
      trace_id: "client-parse",
    },
  });
}

function requireAccessToken():
  | { ok: true; accessToken: string }
  | ApiFailure {
  const accessToken = getAccessToken();
  if (!accessToken) {
    return toApiFailure({
      status: 401,
      body: {
        code: "NO_ACCESS_TOKEN",
        message: "No access token — please log in",
        trace_id: "client-session",
      },
    });
  }
  return { ok: true, accessToken };
}

/** List positions via getPositions (account_id required). */
export async function listPositions(options: {
  accountId: string;
  symbol?: string;
  openOnly?: boolean;
}): Promise<ApiResult<Position[]>> {
  const auth = requireAccessToken();
  if (!auth.ok) return auth;

  const result = await apiCall<unknown>("getPositions", {
    accessToken: auth.accessToken,
    query: {
      account_id: options.accountId,
      symbol: options.symbol,
      open_only: options.openOnly,
    },
  });

  if (!result.ok) return result;

  const list = parsePositionList(result.data);
  if (!list) {
    return invalidBodyFailure(
      result.status,
      "Positions response missing required Position fields",
    );
  }

  return { ok: true, status: result.status, data: list };
}

/** Server-calculated PnL summary via getPnlSummary. */
export async function getPnlSummary(options: {
  accountId: string;
  from?: string;
  to?: string;
}): Promise<ApiResult<PnlSummary>> {
  const auth = requireAccessToken();
  if (!auth.ok) return auth;

  const result = await apiCall<unknown>("getPnlSummary", {
    accessToken: auth.accessToken,
    query: {
      account_id: options.accountId,
      from: options.from,
      to: options.to,
    },
  });

  if (!result.ok) return result;

  const summary = parsePnlSummary(result.data);
  if (!summary) {
    return invalidBodyFailure(
      result.status,
      "PnL summary response missing required PnlSummary fields",
    );
  }

  return { ok: true, status: result.status, data: summary };
}

/** Trade activity via getReportsTrades (account_id required). */
export async function listTradeReports(options: {
  accountId: string;
  strategyId?: string;
  from?: string;
  to?: string;
  limit?: number;
}): Promise<ApiResult<TradeReport[]>> {
  const auth = requireAccessToken();
  if (!auth.ok) return auth;

  const result = await apiCall<unknown>("getReportsTrades", {
    accessToken: auth.accessToken,
    query: {
      account_id: options.accountId,
      strategy_id: options.strategyId,
      from: options.from,
      to: options.to,
      limit: options.limit,
    },
  });

  if (!result.ok) return result;

  const list = parseTradeReportList(result.data);
  if (!list) {
    return invalidBodyFailure(
      result.status,
      "Trade reports response missing required TradeReport fields",
    );
  }

  return { ok: true, status: result.status, data: list };
}

export { formatApiFailureForUi };
export type { ApiFailure };
