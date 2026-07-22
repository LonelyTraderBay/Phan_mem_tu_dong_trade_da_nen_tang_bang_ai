import type { ApiErrorBody } from "./types";

export class ApiError extends Error {
  readonly status: number;
  readonly code: string;
  readonly traceId: string;
  readonly details: ApiErrorBody["details"];
  readonly body: ApiErrorBody | null;

  constructor(status: number, body: ApiErrorBody | null, fallbackMessage?: string) {
    const message = body?.message ?? fallbackMessage ?? `HTTP ${status}`;
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = body?.code ?? `HTTP_${status}`;
    this.traceId = body?.trace_id ?? "";
    this.details = body?.details;
    this.body = body;
  }

  get isUnauthorized(): boolean {
    return this.status === 401;
  }

  get isNotImplemented(): boolean {
    return this.status === 501;
  }
}

/** Human-readable summary for banners — never invent success. */
export function formatApiError(err: unknown): string {
  if (err instanceof ApiError) {
    const parts = [`${err.message} (${err.code})`];
    if (err.status === 501) {
      parts.push("Backend stub not implemented yet.");
    }
    if (err.status === 401) {
      parts.push("Sign in required.");
    }
    if (err.traceId) {
      parts.push(`trace: ${err.traceId}`);
    }
    return parts.join(" — ");
  }
  if (err instanceof Error) {
    return err.message;
  }
  return "Unexpected error";
}
