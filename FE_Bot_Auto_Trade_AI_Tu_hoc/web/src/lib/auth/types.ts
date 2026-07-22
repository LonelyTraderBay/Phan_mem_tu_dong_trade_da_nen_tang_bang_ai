/**
 * Auth shapes from packages/contracts/openapi/openapi.yaml (Auth schemas).
 * Do not invent fields.
 */

export type LoginRequest = {
  email: string;
  password: string;
};

export type RefreshTokenRequest = {
  refresh_token: string;
};

export type LogoutRequest = {
  refresh_token?: string;
};

export type TokenPair = {
  access_token: string;
  refresh_token: string;
  token_type: "Bearer";
  expires_in: number;
};

export type ActionResult = {
  success: boolean;
};

export function parseTokenPair(data: unknown): TokenPair | null {
  if (typeof data !== "object" || data === null) return null;
  const o = data as Record<string, unknown>;
  if (typeof o.access_token !== "string" || o.access_token.length === 0) {
    return null;
  }
  if (typeof o.refresh_token !== "string" || o.refresh_token.length === 0) {
    return null;
  }
  if (o.token_type !== "Bearer") return null;
  if (typeof o.expires_in !== "number" || o.expires_in < 1) return null;
  return {
    access_token: o.access_token,
    refresh_token: o.refresh_token,
    token_type: "Bearer",
    expires_in: o.expires_in,
  };
}

export function parseActionResult(data: unknown): ActionResult | null {
  if (typeof data !== "object" || data === null) return null;
  const o = data as Record<string, unknown>;
  if (typeof o.success !== "boolean") return null;
  return { success: o.success };
}
