/**
 * Gateway Error shape — docs/shared/error-model.md + OpenAPI components.schemas.Error
 */

export type GatewayErrorDetail = {
  field: string;
  reason: string;
};

export type GatewayError = {
  code: string;
  message: string;
  trace_id: string;
  details?: GatewayErrorDetail[];
};

/** UI-facing classification; never invent success. */
export type ApiFailureKind =
  | "stub_not_implemented"
  | "unauthorized"
  | "forbidden"
  | "client_error"
  | "server_error"
  | "network"
  | "invalid_error_body";

export type ApiFailure = {
  ok: false;
  kind: ApiFailureKind;
  status: number | null;
  error: GatewayError;
  /** Raw body text when JSON parse failed (debug only; safe to show trace_id). */
  rawBody?: string;
};

export type ApiSuccess<T> = {
  ok: true;
  status: number;
  data: T;
};

export type ApiResult<T> = ApiSuccess<T> | ApiFailure;

const FALLBACK_CODE = "UNKNOWN_ERROR";

function isDetail(value: unknown): value is GatewayErrorDetail {
  if (typeof value !== "object" || value === null) return false;
  const d = value as Record<string, unknown>;
  return typeof d.field === "string" && typeof d.reason === "string";
}

/**
 * Parse Gateway Error JSON. Returns null if shape is not usable.
 */
export function parseGatewayError(body: unknown): GatewayError | null {
  if (typeof body !== "object" || body === null) return null;
  const o = body as Record<string, unknown>;
  if (typeof o.code !== "string" || typeof o.message !== "string") {
    return null;
  }
  const trace_id =
    typeof o.trace_id === "string" && o.trace_id.length > 0
      ? o.trace_id
      : "";
  if (!trace_id) return null;

  const error: GatewayError = {
    code: o.code,
    message: o.message,
    trace_id,
  };

  if (Array.isArray(o.details)) {
    const details = o.details.filter(isDetail);
    if (details.length > 0) error.details = details;
  }

  return error;
}

export function kindFromHttpStatus(status: number): ApiFailureKind {
  if (status === 501) return "stub_not_implemented";
  if (status === 401) return "unauthorized";
  if (status === 403) return "forbidden";
  if (status >= 400 && status < 500) return "client_error";
  return "server_error";
}

/**
 * Build a structured failure for UI. Does not invent success payloads.
 */
export function toApiFailure(options: {
  status: number | null;
  body?: unknown;
  rawText?: string;
  networkMessage?: string;
}): ApiFailure {
  const { status, body, rawText, networkMessage } = options;

  if (status === null) {
    return {
      ok: false,
      kind: "network",
      status: null,
      error: {
        code: "NETWORK_ERROR",
        message: networkMessage ?? "Network request failed",
        trace_id: "",
      },
      rawBody: rawText,
    };
  }

  const parsed = body !== undefined ? parseGatewayError(body) : null;
  if (parsed) {
    return {
      ok: false,
      kind: kindFromHttpStatus(status),
      status,
      error: parsed,
    };
  }

  return {
    ok: false,
    kind: "invalid_error_body",
    status,
    error: {
      code: status === 501 ? "NOT_IMPLEMENTED" : FALLBACK_CODE,
      message:
        status === 501
          ? "This endpoint is not implemented yet (stub)."
          : `Request failed with HTTP ${status}`,
      trace_id: "",
    },
    rawBody: rawText,
  };
}

/**
 * Short, safe copy for banners/toasts — always surfaces error.code.
 * Special labels for risk_unavailable / kill-switch / not_found so operators
 * never mistake a deny for success.
 */
export function formatApiFailureForUi(failure: ApiFailure): string {
  const { kind, error } = failure;
  if (kind === "stub_not_implemented") {
    return `Chưa sẵn sàng (501) [${error.code}]: ${error.message}`;
  }
  if (kind === "network") {
    return error.message;
  }

  const codeNorm = error.code.toLowerCase();
  const suffix = error.trace_id ? ` (trace: ${error.trace_id})` : "";
  const details =
    error.details && error.details.length > 0
      ? ` — ${error.details.map((d) => `${d.field}: ${d.reason}`).join("; ")}`
      : "";

  let label = `[${error.code}]`;
  if (codeNorm === "risk_unavailable" || codeNorm === "risk_rejected") {
    label = `[${error.code}] Risk unavailable / reject`;
  } else if (
    codeNorm.includes("kill_switch") ||
    codeNorm === "kill_switch_active"
  ) {
    label = `[${error.code}] Kill-switch`;
  } else if (codeNorm === "not_found") {
    label = `[${error.code}] Not found`;
  }

  return `${label}: ${error.message}${details}${suffix}`;
}
