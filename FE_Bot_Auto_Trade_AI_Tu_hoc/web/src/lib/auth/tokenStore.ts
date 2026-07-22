/**
 * SPA token storage (no httpOnly cookies available from pure client).
 * - access_token: in-memory + sessionStorage (survives reload within tab)
 * - refresh_token: in-memory only (minimize XSS / UI exposure; never render)
 */

import type { TokenPair } from "./types";

const ACCESS_STORAGE_KEY = "bat.auth.access_token";
const EXPIRES_STORAGE_KEY = "bat.auth.expires_at";

let accessTokenMem: string | null = null;
/** Refresh stays memory-only — never write to DOM or durable storage. */
let refreshTokenMem: string | null = null;
let expiresAtMs: number | null = null;

function canUseSessionStorage(): boolean {
  return typeof window !== "undefined" && typeof sessionStorage !== "undefined";
}

function hydrateAccessFromSession(): void {
  if (accessTokenMem || !canUseSessionStorage()) return;
  const stored = sessionStorage.getItem(ACCESS_STORAGE_KEY);
  if (stored && stored.length > 0) {
    accessTokenMem = stored;
  }
  const expRaw = sessionStorage.getItem(EXPIRES_STORAGE_KEY);
  if (expRaw) {
    const n = Number(expRaw);
    expiresAtMs = Number.isFinite(n) ? n : null;
  }
}

export function setTokenPair(pair: TokenPair): void {
  accessTokenMem = pair.access_token;
  refreshTokenMem = pair.refresh_token;
  expiresAtMs = Date.now() + pair.expires_in * 1000;

  if (canUseSessionStorage()) {
    sessionStorage.setItem(ACCESS_STORAGE_KEY, pair.access_token);
    sessionStorage.setItem(EXPIRES_STORAGE_KEY, String(expiresAtMs));
  }
}

export function clearTokens(): void {
  accessTokenMem = null;
  refreshTokenMem = null;
  expiresAtMs = null;
  if (canUseSessionStorage()) {
    sessionStorage.removeItem(ACCESS_STORAGE_KEY);
    sessionStorage.removeItem(EXPIRES_STORAGE_KEY);
  }
}

export function getAccessToken(): string | null {
  hydrateAccessFromSession();
  return accessTokenMem;
}

/**
 * For refresh/logout API calls only. Never pass into React props that render text.
 */
export function getRefreshTokenForApi(): string | null {
  return refreshTokenMem;
}

export function hasAccessToken(): boolean {
  return getAccessToken() !== null;
}

export function getAccessExpiresAtMs(): number | null {
  hydrateAccessFromSession();
  return expiresAtMs;
}
