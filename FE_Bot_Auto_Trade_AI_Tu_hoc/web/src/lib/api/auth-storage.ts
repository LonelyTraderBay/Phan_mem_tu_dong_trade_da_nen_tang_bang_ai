/**
 * Token storage: sessionStorage (tab-scoped).
 * - access_token used for Authorization bearer
 * - refresh_token stored for logout/refresh only — NEVER render in UI
 */

const ACCESS_KEY = "trade_ai_access_token";
const REFRESH_KEY = "trade_ai_refresh_token";
const ACCOUNT_KEY = "trade_ai_account_id";

function canUseStorage(): boolean {
  return typeof window !== "undefined" && typeof sessionStorage !== "undefined";
}

export function getAccessToken(): string | null {
  if (!canUseStorage()) return null;
  return sessionStorage.getItem(ACCESS_KEY);
}

export function getRefreshToken(): string | null {
  if (!canUseStorage()) return null;
  return sessionStorage.getItem(REFRESH_KEY);
}

export function setTokenPair(accessToken: string, refreshToken: string): void {
  if (!canUseStorage()) return;
  sessionStorage.setItem(ACCESS_KEY, accessToken);
  sessionStorage.setItem(REFRESH_KEY, refreshToken);
}

export function clearTokens(): void {
  if (!canUseStorage()) return;
  sessionStorage.removeItem(ACCESS_KEY);
  sessionStorage.removeItem(REFRESH_KEY);
}

export function getStoredAccountId(): string {
  if (!canUseStorage()) return "";
  return sessionStorage.getItem(ACCOUNT_KEY) ?? "";
}

export function setStoredAccountId(accountId: string): void {
  if (!canUseStorage()) return;
  if (accountId) {
    sessionStorage.setItem(ACCOUNT_KEY, accountId);
  } else {
    sessionStorage.removeItem(ACCOUNT_KEY);
  }
}

export function isAuthenticated(): boolean {
  return Boolean(getAccessToken());
}
