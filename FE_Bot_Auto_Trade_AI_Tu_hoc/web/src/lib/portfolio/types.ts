/**
 * Portfolio / activity shapes from packages/contracts/openapi/openapi.yaml.
 * Display server fields only — never compute PnL client-side as truth.
 */

export type PositionSide = "long" | "short";

export type TradeSide = "buy" | "sell";

export type Position = {
  id: string;
  account_id: string;
  strategy_id?: string | null;
  symbol: string;
  side: PositionSide;
  quantity: number;
  entry_price: number;
  mark_price?: number;
  unrealized_pnl?: number;
  leverage?: number;
  opened_at: string;
};

export type PnlSummary = {
  account_id: string;
  currency: string;
  realized_pnl: number;
  unrealized_pnl: number;
  total_pnl: number;
  gross_profit?: number;
  gross_loss?: number;
  trade_count?: number;
  calculated_at: string;
};

export type TradeReport = {
  trade_id: string;
  account_id: string;
  strategy_id?: string | null;
  symbol: string;
  side: TradeSide;
  quantity: number;
  price: number;
  fee?: number;
  fee_currency?: string;
  realized_pnl?: number;
  executed_at: string;
};

function isPositionSide(value: unknown): value is PositionSide {
  return value === "long" || value === "short";
}

function isTradeSide(value: unknown): value is TradeSide {
  return value === "buy" || value === "sell";
}

export function parsePosition(data: unknown): Position | null {
  if (typeof data !== "object" || data === null) return null;
  const o = data as Record<string, unknown>;
  if (typeof o.id !== "string" || o.id.length === 0) return null;
  if (typeof o.account_id !== "string" || o.account_id.length === 0) return null;
  if (typeof o.symbol !== "string" || o.symbol.length === 0) return null;
  if (!isPositionSide(o.side)) return null;
  if (typeof o.quantity !== "number" || !Number.isFinite(o.quantity)) return null;
  if (typeof o.entry_price !== "number" || !Number.isFinite(o.entry_price)) {
    return null;
  }
  if (typeof o.opened_at !== "string") return null;

  const position: Position = {
    id: o.id,
    account_id: o.account_id,
    symbol: o.symbol,
    side: o.side,
    quantity: o.quantity,
    entry_price: o.entry_price,
    opened_at: o.opened_at,
  };
  if (o.strategy_id === null) {
    position.strategy_id = null;
  } else if (typeof o.strategy_id === "string") {
    position.strategy_id = o.strategy_id;
  }
  if (typeof o.mark_price === "number" && Number.isFinite(o.mark_price)) {
    position.mark_price = o.mark_price;
  }
  if (
    typeof o.unrealized_pnl === "number" &&
    Number.isFinite(o.unrealized_pnl)
  ) {
    position.unrealized_pnl = o.unrealized_pnl;
  }
  if (typeof o.leverage === "number" && Number.isFinite(o.leverage)) {
    position.leverage = o.leverage;
  }
  return position;
}

export function parsePositionList(data: unknown): Position[] | null {
  if (!Array.isArray(data)) return null;
  const list: Position[] = [];
  for (const item of data) {
    const parsed = parsePosition(item);
    if (!parsed) return null;
    list.push(parsed);
  }
  return list;
}

export function parsePnlSummary(data: unknown): PnlSummary | null {
  if (typeof data !== "object" || data === null) return null;
  const o = data as Record<string, unknown>;
  if (typeof o.account_id !== "string" || o.account_id.length === 0) return null;
  if (typeof o.currency !== "string") return null;
  if (typeof o.realized_pnl !== "number" || !Number.isFinite(o.realized_pnl)) {
    return null;
  }
  if (
    typeof o.unrealized_pnl !== "number" ||
    !Number.isFinite(o.unrealized_pnl)
  ) {
    return null;
  }
  if (typeof o.total_pnl !== "number" || !Number.isFinite(o.total_pnl)) {
    return null;
  }
  if (typeof o.calculated_at !== "string") return null;

  const summary: PnlSummary = {
    account_id: o.account_id,
    currency: o.currency,
    realized_pnl: o.realized_pnl,
    unrealized_pnl: o.unrealized_pnl,
    total_pnl: o.total_pnl,
    calculated_at: o.calculated_at,
  };
  if (typeof o.gross_profit === "number" && Number.isFinite(o.gross_profit)) {
    summary.gross_profit = o.gross_profit;
  }
  if (typeof o.gross_loss === "number" && Number.isFinite(o.gross_loss)) {
    summary.gross_loss = o.gross_loss;
  }
  if (typeof o.trade_count === "number" && Number.isFinite(o.trade_count)) {
    summary.trade_count = o.trade_count;
  }
  return summary;
}

export function parseTradeReport(data: unknown): TradeReport | null {
  if (typeof data !== "object" || data === null) return null;
  const o = data as Record<string, unknown>;
  if (typeof o.trade_id !== "string" || o.trade_id.length === 0) return null;
  if (typeof o.account_id !== "string" || o.account_id.length === 0) return null;
  if (typeof o.symbol !== "string" || o.symbol.length === 0) return null;
  if (!isTradeSide(o.side)) return null;
  if (typeof o.quantity !== "number" || !Number.isFinite(o.quantity)) return null;
  if (typeof o.price !== "number" || !Number.isFinite(o.price)) return null;
  if (typeof o.executed_at !== "string") return null;

  const trade: TradeReport = {
    trade_id: o.trade_id,
    account_id: o.account_id,
    symbol: o.symbol,
    side: o.side,
    quantity: o.quantity,
    price: o.price,
    executed_at: o.executed_at,
  };
  if (o.strategy_id === null) {
    trade.strategy_id = null;
  } else if (typeof o.strategy_id === "string") {
    trade.strategy_id = o.strategy_id;
  }
  if (typeof o.fee === "number" && Number.isFinite(o.fee)) {
    trade.fee = o.fee;
  }
  if (typeof o.fee_currency === "string") {
    trade.fee_currency = o.fee_currency;
  }
  if (typeof o.realized_pnl === "number" && Number.isFinite(o.realized_pnl)) {
    trade.realized_pnl = o.realized_pnl;
  }
  return trade;
}

export function parseTradeReportList(data: unknown): TradeReport[] | null {
  if (!Array.isArray(data)) return null;
  const list: TradeReport[] = [];
  for (const item of data) {
    const parsed = parseTradeReport(item);
    if (!parsed) return null;
    list.push(parsed);
  }
  return list;
}
