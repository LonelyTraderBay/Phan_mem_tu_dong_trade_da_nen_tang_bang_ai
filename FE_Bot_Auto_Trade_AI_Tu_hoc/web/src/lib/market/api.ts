/**
 * Market API — OpenAPI getMarketSymbols / getMarketCandles only.
 * Reads X-Market-Stale response header; never fabricates OHLCV.
 */

import {
  apiRequest,
  formatApiFailureForUi,
  toApiFailure,
  type ApiFailure,
} from "@/lib/api/client";
import { getAccessToken } from "@/lib/auth/tokenStore";
import {
  parseCandleList,
  parseMarketSymbolList,
  type Candle,
  type CandleInterval,
  type MarketSymbol,
  type MarketType,
} from "./types";

/** Success may still be stale when gateway sends X-Market-Stale. */
export type MarketApiSuccess<T> = {
  ok: true;
  status: number;
  data: T;
  stale: boolean;
};

export type MarketApiResult<T> = MarketApiSuccess<T> | ApiFailure;

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

/** True when gateway marks the feed stale via X-Market-Stale. */
export function isMarketStaleHeader(headers: Headers): boolean {
  const raw = headers.get("X-Market-Stale");
  if (raw === null) return false;
  const v = raw.trim().toLowerCase();
  return v === "true" || v === "1" || v === "yes";
}

async function marketRequest(
  operationId: "getMarketSymbols" | "getMarketCandles",
  options: {
    accessToken: string;
    query?: Record<string, string | number | boolean | undefined | null>;
  },
): Promise<
  | { ok: true; status: number; body: unknown; stale: boolean }
  | ApiFailure
> {
  let response: Response;
  try {
    response = await apiRequest(operationId, {
      accessToken: options.accessToken,
      query: options.query,
    });
  } catch (err) {
    return toApiFailure({
      status: null,
      networkMessage:
        err instanceof Error ? err.message : "Network request failed",
    });
  }

  const rawText = await response.text();
  let body: unknown = undefined;
  if (rawText.length > 0) {
    try {
      body = JSON.parse(rawText) as unknown;
    } catch {
      body = undefined;
    }
  }

  if (!response.ok) {
    return toApiFailure({
      status: response.status,
      body,
      rawText: rawText.length > 0 ? rawText : undefined,
    });
  }

  return {
    ok: true,
    status: response.status,
    body,
    stale: isMarketStaleHeader(response.headers),
  };
}

/** List symbols via getMarketSymbols. */
export async function listMarketSymbols(options?: {
  exchange?: string;
  marketType?: MarketType;
}): Promise<MarketApiResult<MarketSymbol[]>> {
  const auth = requireAccessToken();
  if (!auth.ok) return auth;

  const result = await marketRequest("getMarketSymbols", {
    accessToken: auth.accessToken,
    query: {
      exchange: options?.exchange,
      market_type: options?.marketType,
    },
  });

  if (!result.ok) return result;

  const list = parseMarketSymbolList(result.body);
  if (!list) {
    return invalidBodyFailure(
      result.status,
      "Market symbols response missing required MarketSymbol fields",
    );
  }

  return {
    ok: true,
    status: result.status,
    data: list,
    stale: result.stale,
  };
}

/** OHLCV candles via getMarketCandles. Empty array only from server — never invent. */
export async function listMarketCandles(options: {
  symbol: string;
  interval: CandleInterval;
  startTime?: string;
  endTime?: string;
  limit?: number;
}): Promise<MarketApiResult<Candle[]>> {
  const auth = requireAccessToken();
  if (!auth.ok) return auth;

  const result = await marketRequest("getMarketCandles", {
    accessToken: auth.accessToken,
    query: {
      symbol: options.symbol,
      interval: options.interval,
      start_time: options.startTime,
      end_time: options.endTime,
      limit: options.limit,
    },
  });

  if (!result.ok) return result;

  const list = parseCandleList(result.body);
  if (!list) {
    return invalidBodyFailure(
      result.status,
      "Candles response missing required Candle fields",
    );
  }

  return {
    ok: true,
    status: result.status,
    data: list,
    stale: result.stale,
  };
}

export { formatApiFailureForUi };
export type { ApiFailure };
