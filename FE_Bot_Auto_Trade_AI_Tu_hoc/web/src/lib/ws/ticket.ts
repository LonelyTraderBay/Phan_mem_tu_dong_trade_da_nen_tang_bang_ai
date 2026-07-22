import { apiCall, toApiFailure, type ApiResult } from "@/lib/api/client";
import { getAccessToken } from "@/lib/auth/tokenStore";
import { parseWsTicket, type WsTicketResponse } from "./types";

export async function postWsTicket(): Promise<ApiResult<WsTicketResponse>> {
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

  const result = await apiCall<unknown>("postWsTicket", { accessToken });
  if (!result.ok) return result;

  const parsed = parseWsTicket(result.data);
  if (!parsed) {
    return toApiFailure({
      status: result.status,
      body: {
        code: "INVALID_RESPONSE",
        message: "WsTicketResponse missing required fields",
        trace_id: "client-parse",
      },
    });
  }
  return { ok: true, status: result.status, data: parsed };
}
