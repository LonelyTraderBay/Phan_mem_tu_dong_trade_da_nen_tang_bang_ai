/**
 * Operator auth session — OpenAPI postAuthLogin / postAuthRefresh / postAuthLogout.
 */

import {
  apiCall,
  formatApiFailureForUi,
  toApiFailure,
  type ApiResult,
} from "@/lib/api/client";
import {
  clearTokens,
  getAccessToken,
  getRefreshTokenForApi,
  setTokenPair,
} from "./tokenStore";
import {
  parseActionResult,
  parseTokenPair,
  type ActionResult,
  type LoginRequest,
  type TokenPair,
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

/**
 * Login with email+password. Stores tokens on schema-valid 2xx only.
 * Never invents success from empty/invalid bodies.
 */
export async function login(
  credentials: LoginRequest,
): Promise<ApiResult<TokenPair>> {
  const result = await apiCall<unknown>("postAuthLogin", {
    body: credentials,
  });

  if (!result.ok) return result;

  const pair = parseTokenPair(result.data);
  if (!pair) {
    return invalidBodyFailure(
      result.status,
      "Login response missing required TokenPair fields",
    );
  }

  setTokenPair(pair);
  return { ok: true, status: result.status, data: pair };
}

/**
 * Refresh access token via postAuthRefresh. Requires in-memory refresh token.
 */
export async function refreshSession(): Promise<ApiResult<TokenPair>> {
  const refresh_token = getRefreshTokenForApi();
  if (!refresh_token) {
    return toApiFailure({
      status: 401,
      body: {
        code: "NO_REFRESH_TOKEN",
        message: "No refresh token in session — please log in again",
        trace_id: "client-session",
      },
    });
  }

  const result = await apiCall<unknown>("postAuthRefresh", {
    body: { refresh_token },
  });

  if (!result.ok) {
    if (result.kind === "unauthorized") {
      clearTokens();
    }
    return result;
  }

  const pair = parseTokenPair(result.data);
  if (!pair) {
    return invalidBodyFailure(
      result.status,
      "Refresh response missing required TokenPair fields",
    );
  }

  setTokenPair(pair);
  return { ok: true, status: result.status, data: pair };
}

/**
 * Logout via postAuthLogout, then always clear local tokens.
 */
export async function logout(): Promise<ApiResult<ActionResult>> {
  const accessToken = getAccessToken() ?? undefined;
  const refresh_token = getRefreshTokenForApi();
  const body = refresh_token ? { refresh_token } : undefined;

  const result = await apiCall<unknown>("postAuthLogout", {
    accessToken,
    body,
  });

  clearTokens();

  if (!result.ok) return result;

  const action = parseActionResult(result.data);
  if (!action) {
    return invalidBodyFailure(
      result.status,
      "Logout response missing required ActionResult fields",
    );
  }

  return { ok: true, status: result.status, data: action };
}

export { formatApiFailureForUi };
