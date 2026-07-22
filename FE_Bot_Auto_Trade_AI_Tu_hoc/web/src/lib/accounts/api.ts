/**
 * Accounts API — OpenAPI postAccounts / postAccountApiKeys.
 * Secrets never logged; callers must clear secret inputs after success.
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
  parseAccount,
  parseApiKeyMasked,
  type Account,
  type AccountCreate,
  type ApiKeyCreate,
  type ApiKeyMasked,
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

/** Create trading account via postAccounts. */
export async function createAccount(
  body: AccountCreate,
): Promise<ApiResult<Account>> {
  const auth = requireAccessToken();
  if (!auth.ok) return auth;

  const result = await apiCall<unknown>("postAccounts", {
    accessToken: auth.accessToken,
    body,
  });

  if (!result.ok) return result;

  const account = parseAccount(result.data);
  if (!account) {
    return invalidBodyFailure(
      result.status,
      "Account response missing required Account fields",
    );
  }

  return { ok: true, status: result.status, data: account };
}

/**
 * Register exchange API credentials via postAccountApiKeys.
 * Response is masked only — never expect full secret back.
 */
export async function createAccountApiKey(
  accountId: string,
  body: ApiKeyCreate,
): Promise<ApiResult<ApiKeyMasked>> {
  const auth = requireAccessToken();
  if (!auth.ok) return auth;

  const result = await apiCall<unknown>("postAccountApiKeys", {
    accessToken: auth.accessToken,
    pathParams: { account_id: accountId },
    body,
  });

  if (!result.ok) return result;

  const masked = parseApiKeyMasked(result.data);
  if (!masked) {
    return invalidBodyFailure(
      result.status,
      "API key response missing required ApiKeyMasked fields",
    );
  }

  return { ok: true, status: result.status, data: masked };
}

export { formatApiFailureForUi };
