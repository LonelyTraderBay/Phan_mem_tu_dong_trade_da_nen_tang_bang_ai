/**
 * Alerts API — OpenAPI getAlerts.
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
  parseAlertList,
  type Alert,
  type AlertSeverity,
} from "./types";

export type GetAlertsQuery = {
  account_id?: string;
  acknowledged?: boolean;
  severity?: AlertSeverity;
  limit?: number;
};

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

/** GET /v1/alerts */
export async function getAlerts(
  query: GetAlertsQuery = {},
): Promise<ApiResult<Alert[]>> {
  const auth = requireAccessToken();
  if (!auth.ok) return auth;

  const result = await apiCall<unknown>("getAlerts", {
    accessToken: auth.accessToken,
    query: {
      account_id: query.account_id,
      acknowledged: query.acknowledged,
      severity: query.severity,
      limit: query.limit,
    },
  });

  if (!result.ok) return result;

  const list = parseAlertList(result.data);
  if (!list) {
    return invalidBodyFailure(
      result.status,
      "Alerts response missing required Alert array fields",
    );
  }

  return { ok: true, status: result.status, data: list };
}

export { formatApiFailureForUi };
