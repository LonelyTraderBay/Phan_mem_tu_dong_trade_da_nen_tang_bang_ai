/**
 * Kill-switch shapes from packages/contracts/openapi/openapi.yaml.
 * MVP: engaged boolean maps to L1 pause (emergency pause new entries).
 */

export type KillSwitchRequest = {
  engaged: boolean;
  reason: string;
};

export type KillSwitchStatus = {
  engaged: boolean;
  reason: string | null;
  updated_at: string;
  updated_by: string | null;
};

export function parseKillSwitchStatus(data: unknown): KillSwitchStatus | null {
  if (typeof data !== "object" || data === null) return null;
  const o = data as Record<string, unknown>;
  if (typeof o.engaged !== "boolean") return null;
  if (typeof o.updated_at !== "string" || o.updated_at.length === 0) return null;

  const reason =
    o.reason === null || o.reason === undefined
      ? null
      : typeof o.reason === "string"
        ? o.reason
        : null;
  if (o.reason !== null && o.reason !== undefined && reason === null) {
    return null;
  }

  const updated_by =
    o.updated_by === null || o.updated_by === undefined
      ? null
      : typeof o.updated_by === "string"
        ? o.updated_by
        : null;
  if (
    o.updated_by !== null &&
    o.updated_by !== undefined &&
    updated_by === null
  ) {
    return null;
  }

  return {
    engaged: o.engaged,
    reason,
    updated_at: o.updated_at,
    updated_by,
  };
}
