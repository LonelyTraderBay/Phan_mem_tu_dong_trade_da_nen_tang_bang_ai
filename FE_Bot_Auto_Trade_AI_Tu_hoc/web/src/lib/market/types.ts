/**
 * Market shapes from packages/contracts/openapi/openapi.yaml.
 * Do not invent fields or fabricate OHLCV.
 */

export type MarketType = "spot" | "futures";

export type CandleInterval = "1m" | "5m" | "15m" | "1h" | "4h" | "1d";

export type MarketSymbol = {
  symbol: string;
  base_asset: string;
  quote_asset: string;
  exchange: string;
  market_type: MarketType;
  active: boolean;
  price_precision?: number;
  quantity_precision?: number;
};

export type Candle = {
  symbol: string;
  interval: string;
  open_time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  close_time?: string;
};

export const CANDLE_INTERVALS: CandleInterval[] = [
  "1m",
  "5m",
  "15m",
  "1h",
  "4h",
  "1d",
];

function isMarketType(value: unknown): value is MarketType {
  return value === "spot" || value === "futures";
}

export function parseMarketSymbol(data: unknown): MarketSymbol | null {
  if (typeof data !== "object" || data === null) return null;
  const o = data as Record<string, unknown>;
  if (typeof o.symbol !== "string" || o.symbol.length === 0) return null;
  if (typeof o.base_asset !== "string") return null;
  if (typeof o.quote_asset !== "string") return null;
  if (typeof o.exchange !== "string") return null;
  if (!isMarketType(o.market_type)) return null;
  if (typeof o.active !== "boolean") return null;

  const symbol: MarketSymbol = {
    symbol: o.symbol,
    base_asset: o.base_asset,
    quote_asset: o.quote_asset,
    exchange: o.exchange,
    market_type: o.market_type,
    active: o.active,
  };
  if (typeof o.price_precision === "number") {
    symbol.price_precision = o.price_precision;
  }
  if (typeof o.quantity_precision === "number") {
    symbol.quantity_precision = o.quantity_precision;
  }
  return symbol;
}

export function parseMarketSymbolList(data: unknown): MarketSymbol[] | null {
  if (!Array.isArray(data)) return null;
  const list: MarketSymbol[] = [];
  for (const item of data) {
    const parsed = parseMarketSymbol(item);
    if (!parsed) return null;
    list.push(parsed);
  }
  return list;
}

export function parseCandle(data: unknown): Candle | null {
  if (typeof data !== "object" || data === null) return null;
  const o = data as Record<string, unknown>;
  if (typeof o.symbol !== "string" || o.symbol.length === 0) return null;
  if (typeof o.interval !== "string") return null;
  if (typeof o.open_time !== "string") return null;
  if (typeof o.open !== "number" || !Number.isFinite(o.open)) return null;
  if (typeof o.high !== "number" || !Number.isFinite(o.high)) return null;
  if (typeof o.low !== "number" || !Number.isFinite(o.low)) return null;
  if (typeof o.close !== "number" || !Number.isFinite(o.close)) return null;
  if (typeof o.volume !== "number" || !Number.isFinite(o.volume)) return null;

  const candle: Candle = {
    symbol: o.symbol,
    interval: o.interval,
    open_time: o.open_time,
    open: o.open,
    high: o.high,
    low: o.low,
    close: o.close,
    volume: o.volume,
  };
  if (typeof o.close_time === "string") {
    candle.close_time = o.close_time;
  }
  return candle;
}

export function parseCandleList(data: unknown): Candle[] | null {
  if (!Array.isArray(data)) return null;
  const list: Candle[] = [];
  for (const item of data) {
    const parsed = parseCandle(item);
    if (!parsed) return null;
    list.push(parsed);
  }
  return list;
}
