/**
 * Alert shapes from packages/contracts/openapi/openapi.yaml.
 */

export type AlertSeverity = "info" | "warning" | "critical";

export type Alert = {
  id: string;
  account_id: string | null;
  severity: AlertSeverity;
  code: string;
  message: string;
  acknowledged: boolean;
  created_at: string;
  acknowledged_at: string | null;
};

export const ALERT_SEVERITIES: AlertSeverity[] = [
  "info",
  "warning",
  "critical",
];

function isAlertSeverity(value: unknown): value is AlertSeverity {
  return value === "info" || value === "warning" || value === "critical";
}

export function parseAlert(data: unknown): Alert | null {
  if (typeof data !== "object" || data === null) return null;
  const o = data as Record<string, unknown>;
  if (typeof o.id !== "string" || o.id.length === 0) return null;
  if (!isAlertSeverity(o.severity)) return null;
  if (typeof o.code !== "string") return null;
  if (typeof o.message !== "string") return null;
  if (typeof o.acknowledged !== "boolean") return null;
  if (typeof o.created_at !== "string") return null;

  const account_id =
    o.account_id === null || o.account_id === undefined
      ? null
      : typeof o.account_id === "string"
        ? o.account_id
        : null;
  if (
    o.account_id !== null &&
    o.account_id !== undefined &&
    account_id === null
  ) {
    return null;
  }

  const acknowledged_at =
    o.acknowledged_at === null || o.acknowledged_at === undefined
      ? null
      : typeof o.acknowledged_at === "string"
        ? o.acknowledged_at
        : null;
  if (
    o.acknowledged_at !== null &&
    o.acknowledged_at !== undefined &&
    acknowledged_at === null
  ) {
    return null;
  }

  return {
    id: o.id,
    account_id,
    severity: o.severity,
    code: o.code,
    message: o.message,
    acknowledged: o.acknowledged,
    created_at: o.created_at,
    acknowledged_at,
  };
}

export function parseAlertList(data: unknown): Alert[] | null {
  if (!Array.isArray(data)) return null;
  const list: Alert[] = [];
  for (const item of data) {
    const parsed = parseAlert(item);
    if (!parsed) return null;
    list.push(parsed);
  }
  return list;
}
