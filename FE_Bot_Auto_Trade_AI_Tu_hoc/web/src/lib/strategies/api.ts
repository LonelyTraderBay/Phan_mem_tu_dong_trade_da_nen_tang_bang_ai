/**
 * Strategies API — OpenAPI getStrategies / postStrategies / patchStrategy.
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
  parseStrategy,
  parseStrategyList,
  type Strategy,
  type StrategyCreate,
  type StrategyPatch,
  type StrategyStatus,
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

/** List strategies via getStrategies (account_id query required by OpenAPI). */
export async function listStrategies(options: {
  accountId: string;
  status?: StrategyStatus;
}): Promise<ApiResult<Strategy[]>> {
  const auth = requireAccessToken();
  if (!auth.ok) return auth;

  const result = await apiCall<unknown>("getStrategies", {
    accessToken: auth.accessToken,
    query: {
      account_id: options.accountId,
      status: options.status,
    },
  });

  if (!result.ok) return result;

  const list = parseStrategyList(result.data);
  if (!list) {
    return invalidBodyFailure(
      result.status,
      "Strategies response missing required Strategy fields",
    );
  }

  return { ok: true, status: result.status, data: list };
}

/** Create a strategy via postStrategies. */
export async function createStrategy(
  body: StrategyCreate,
): Promise<ApiResult<Strategy>> {
  const auth = requireAccessToken();
  if (!auth.ok) return auth;

  const result = await apiCall<unknown>("postStrategies", {
    accessToken: auth.accessToken,
    body,
  });

  if (!result.ok) return result;

  const strategy = parseStrategy(result.data);
  if (!strategy) {
    return invalidBodyFailure(
      result.status,
      "Strategy response missing required Strategy fields",
    );
  }

  return { ok: true, status: result.status, data: strategy };
}

/** Update a strategy via patchStrategy (e.g. status start/stop/pause). */
export async function patchStrategy(
  strategyId: string,
  body: StrategyPatch,
): Promise<ApiResult<Strategy>> {
  const auth = requireAccessToken();
  if (!auth.ok) return auth;

  const result = await apiCall<unknown>("patchStrategy", {
    accessToken: auth.accessToken,
    pathParams: { strategy_id: strategyId },
    body,
  });

  if (!result.ok) return result;

  const strategy = parseStrategy(result.data);
  if (!strategy) {
    return invalidBodyFailure(
      result.status,
      "Strategy response missing required Strategy fields",
    );
  }

  return { ok: true, status: result.status, data: strategy };
}

export { formatApiFailureForUi };
