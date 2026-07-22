/**
 * Strategy shapes from packages/contracts/openapi/openapi.yaml.
 * Do not invent fields. No-code builder is Deferred — form fields only.
 */

export type StrategyStatus = "draft" | "active" | "paused" | "stopped";

export type StrategyTimeframe = "1m" | "5m" | "15m" | "1h" | "4h" | "1d";

export type StrategyCreate = {
  account_id: string;
  name: string;
  symbol: string;
  timeframe: StrategyTimeframe;
  status?: StrategyStatus;
  max_position_size?: number;
  stop_loss_percent?: number;
};

export type StrategyPatch = {
  name?: string;
  status?: StrategyStatus;
  timeframe?: StrategyTimeframe;
  max_position_size?: number;
  stop_loss_percent?: number;
};

export type Strategy = {
  id: string;
  account_id: string;
  name: string;
  symbol: string;
  timeframe: string;
  status: StrategyStatus;
  created_at: string;
  max_position_size?: number;
  stop_loss_percent?: number;
  updated_at?: string;
};

export const STRATEGY_STATUSES: StrategyStatus[] = [
  "draft",
  "active",
  "paused",
  "stopped",
];

export const STRATEGY_TIMEFRAMES: StrategyTimeframe[] = [
  "1m",
  "5m",
  "15m",
  "1h",
  "4h",
  "1d",
];

/** Statuses used for start / pause / stop controls (not draft). */
export const STRATEGY_RUN_STATUSES: StrategyStatus[] = [
  "active",
  "paused",
  "stopped",
];

function isStrategyStatus(value: unknown): value is StrategyStatus {
  return (
    value === "draft" ||
    value === "active" ||
    value === "paused" ||
    value === "stopped"
  );
}

export function parseStrategy(data: unknown): Strategy | null {
  if (typeof data !== "object" || data === null) return null;
  const o = data as Record<string, unknown>;
  if (typeof o.id !== "string" || o.id.length === 0) return null;
  if (typeof o.account_id !== "string" || o.account_id.length === 0) return null;
  if (typeof o.name !== "string") return null;
  if (typeof o.symbol !== "string") return null;
  if (typeof o.timeframe !== "string") return null;
  if (!isStrategyStatus(o.status)) return null;
  if (typeof o.created_at !== "string") return null;

  const strategy: Strategy = {
    id: o.id,
    account_id: o.account_id,
    name: o.name,
    symbol: o.symbol,
    timeframe: o.timeframe,
    status: o.status,
    created_at: o.created_at,
  };
  if (typeof o.max_position_size === "number") {
    strategy.max_position_size = o.max_position_size;
  }
  if (typeof o.stop_loss_percent === "number") {
    strategy.stop_loss_percent = o.stop_loss_percent;
  }
  if (typeof o.updated_at === "string") {
    strategy.updated_at = o.updated_at;
  }
  return strategy;
}

export function parseStrategyList(data: unknown): Strategy[] | null {
  if (!Array.isArray(data)) return null;
  const list: Strategy[] = [];
  for (const item of data) {
    const parsed = parseStrategy(item);
    if (!parsed) return null;
    list.push(parsed);
  }
  return list;
}
