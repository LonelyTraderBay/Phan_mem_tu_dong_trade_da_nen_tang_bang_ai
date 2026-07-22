/**
 * Kill-switch API — OpenAPI getKillSwitchStatus / postKillSwitch.
 * L1 pause = engaged true (stop new entries).
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
  parseKillSwitchStatus,
  type KillSwitchRequest,
  type KillSwitchStatus,
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

/** GET /v1/kill-switch */
export async function getKillSwitchStatus(): Promise<
  ApiResult<KillSwitchStatus>
> {
  const auth = requireAccessToken();
  if (!auth.ok) return auth;

  const result = await apiCall<unknown>("getKillSwitchStatus", {
    accessToken: auth.accessToken,
  });

  if (!result.ok) return result;

  const status = parseKillSwitchStatus(result.data);
  if (!status) {
    return invalidBodyFailure(
      result.status,
      "Kill-switch response missing required KillSwitchStatus fields",
    );
  }

  return { ok: true, status: result.status, data: status };
}

/** POST /v1/kill-switch — caller MUST confirm in UI before calling. */
export async function postKillSwitch(
  body: KillSwitchRequest,
): Promise<ApiResult<KillSwitchStatus>> {
  const auth = requireAccessToken();
  if (!auth.ok) return auth;

  const result = await apiCall<unknown>("postKillSwitch", {
    accessToken: auth.accessToken,
    body,
  });

  if (!result.ok) return result;

  const status = parseKillSwitchStatus(result.data);
  if (!status) {
    return invalidBodyFailure(
      result.status,
      "Kill-switch response missing required KillSwitchStatus fields",
    );
  }

  return { ok: true, status: result.status, data: status };
}

export { formatApiFailureForUi };
