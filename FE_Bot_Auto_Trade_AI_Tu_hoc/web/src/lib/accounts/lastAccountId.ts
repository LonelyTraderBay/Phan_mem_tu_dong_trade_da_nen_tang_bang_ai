/**
 * Remember last paper Account ID for UX prefill (session only).
 * Not a source of truth — OpenAPI still requires account_id on each call.
 */

const STORAGE_KEY = "bat.paper.last_account_id";

function canUseSessionStorage(): boolean {
  return typeof window !== "undefined" && typeof sessionStorage !== "undefined";
}

export function getLastAccountId(): string | null {
  if (!canUseSessionStorage()) return null;
  const v = sessionStorage.getItem(STORAGE_KEY);
  return v && v.trim().length > 0 ? v.trim() : null;
}

export function setLastAccountId(accountId: string): void {
  const id = accountId.trim();
  if (!id || !canUseSessionStorage()) return;
  sessionStorage.setItem(STORAGE_KEY, id);
}

export function clearLastAccountId(): void {
  if (!canUseSessionStorage()) return;
  sessionStorage.removeItem(STORAGE_KEY);
}
