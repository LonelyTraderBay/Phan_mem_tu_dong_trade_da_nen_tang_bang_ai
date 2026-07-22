/**
 * Kill-switch shapes from packages/contracts/openapi/openapi.yaml (0.2.0+).
 */

export type KillSwitchLevel = "L1" | "L2" | "L3" | "L4";

export type KillSwitchRequest = {
  engaged: boolean;
  reason: string;
  level?: KillSwitchLevel;
  confirmed?: boolean;
};

export type KillSwitchStatus = {
  engaged: boolean;
  level: KillSwitchLevel | null;
  reason: string | null;
  updated_at: string;
  updated_by: string | null;
  trace_id: string | null;
};

const LEVELS = new Set<string>(["L1", "L2", "L3", "L4"]);

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

  let level: KillSwitchLevel | null = null;
  if (o.level !== null && o.level !== undefined) {
    if (typeof o.level !== "string" || !LEVELS.has(o.level)) return null;
    level = o.level as KillSwitchLevel;
  }

  const trace_id =
    o.trace_id === null || o.trace_id === undefined
      ? null
      : typeof o.trace_id === "string"
        ? o.trace_id
        : null;
  if (o.trace_id !== null && o.trace_id !== undefined && trace_id === null) {
    return null;
  }

  return {
    engaged: o.engaged,
    level,
    reason,
    updated_at: o.updated_at,
    updated_by,
    trace_id,
  };
}
