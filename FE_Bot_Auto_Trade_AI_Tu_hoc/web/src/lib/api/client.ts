/**
 * Gateway HTTP client - paths from OpenAPI operation map only.
 * Errors: docs/shared/error-model.md (code, message, trace_id, details).
 */

import {
  API_OPERATIONS,
  type OperationId,
  resolveOperationPath,
} from "./operations";
import {
  type ApiResult,
  toApiFailure,
} from "./errors";

const fetchBase =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export function getApiBaseUrl(): string {
  return fetchBase;
}

export function getWsBaseUrl(): string {
  return process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:8000/ws";
}

function joinUrl(path: string): string {
  return `${fetchBase.replace(/\/$/, "")}/${path.replace(/^\//, "")}`;
}

/**
 * Low-level fetch by relative path. Prefer `apiRequest` / `apiCall` so callers
 * stay on known OpenAPI operations.
 */
export async function apiFetch(
  path: string,
  init?: RequestInit,
): Promise<Response> {
  return fetch(joinUrl(path), init);
}

export type ApiCallOptions = {
  pathParams?: Record<string, string>;
  query?: Record<string, string | number | boolean | undefined | null>;
  body?: unknown;
  headers?: HeadersInit;
  signal?: AbortSignal;
  /** Bearer access token when required by the operation. */
  accessToken?: string;
};

function buildQuery(
  query?: ApiCallOptions["query"],
): string {
  if (!query) return "";
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(query)) {
    if (value === undefined || value === null) continue;
    params.set(key, String(value));
  }
  const s = params.toString();
  return s ? `?${s}` : "";
}

/**
 * Call a known OpenAPI operation. Returns raw Response (caller parses).
 * Throws if path params are missing for templated paths.
 */
export async function apiRequest(
  operationId: OperationId,
  options: ApiCallOptions = {},
): Promise<Response> {
  const op = API_OPERATIONS[operationId];
  const path =
    resolveOperationPath(op.path, options.pathParams) +
    buildQuery(options.query);

  const headers = new Headers(options.headers);
  if (options.body !== undefined && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  if (options.accessToken) {
    headers.set("Authorization", `Bearer ${options.accessToken}`);
  }

  return apiFetch(path, {
    method: op.method,
    headers,
    body:
      options.body === undefined ? undefined : JSON.stringify(options.body),
    signal: options.signal,
  });
}

/**
 * Typed-ish helper: parses JSON on 2xx; on any other status returns structured
 * ApiFailure (501 → stub_not_implemented). Never invents success data.
 */
export async function apiCall<T = unknown>(
  operationId: OperationId,
  options: ApiCallOptions = {},
): Promise<ApiResult<T>> {
  let response: Response;
  try {
    response = await apiRequest(operationId, options);
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

  if (response.ok) {
    return {
      ok: true,
      status: response.status,
      data: (body === undefined ? null : body) as T,
    };
  }

  return toApiFailure({
    status: response.status,
    body,
    rawText: rawText.length > 0 ? rawText : undefined,
  });
}

export { API_OPERATIONS } from "./operations";
export type { OperationId, ApiOperation, HttpMethod } from "./operations";
export {
  parseGatewayError,
  toApiFailure,
  formatApiFailureForUi,
  kindFromHttpStatus,
} from "./errors";
export type {
  GatewayError,
  GatewayErrorDetail,
  ApiFailure,
  ApiFailureKind,
  ApiResult,
  ApiSuccess,
} from "./errors";
