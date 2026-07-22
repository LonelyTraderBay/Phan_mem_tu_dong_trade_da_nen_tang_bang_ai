/**
 * MVP OpenAPI schema types (packages/contracts/openapi/openapi.yaml).
 * Only shapes used by In-MVP operationIds.
 */

export type ErrorDetail = {
  field: string;
  reason: string;
};

/** docs/shared/error-model.md + components.schemas.Error */
export type ApiErrorBody = {
  code: string;
  message: string;
  trace_id: string;
  details?: ErrorDetail[];
};

export type ActionResult = {
  success: boolean;
};

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

export type MarketType = "spot" | "futures";

export type AccountCreate = {
  name: string;
  exchange: string;
  market_type: MarketType;
  testnet?: boolean;
};

export type AccountStatus = "active" | "disabled" | "error";

export type Account = {
  id: string;
  name: string;
  exchange: string;
  market_type: MarketType;
  testnet: boolean;
  status: AccountStatus;
  created_at: string;
  updated_at?: string;
};

export type ApiKeyCreate = {
  label: string;
  api_key: string;
  api_secret: string;
  passphrase?: string;
};

export type ApiKeyMasked = {
  id: string;
  account_id: string;
  label: string;
  masked_api_key: string;
  created_at: string;
  last_validated_at?: string | null;
};

export type StrategyStatus = "draft" | "active" | "paused" | "stopped";

export type CandleInterval = "1m" | "5m" | "15m" | "1h" | "4h" | "1d";

export type StrategyCreate = {
  account_id: string;
  name: string;
  symbol: string;
  timeframe: CandleInterval;
  status?: StrategyStatus;
  max_position_size?: number;
  stop_loss_percent?: number;
};

export type StrategyPatch = {
  name?: string;
  status?: StrategyStatus;
  timeframe?: CandleInterval;
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
  max_position_size?: number;
  stop_loss_percent?: number;
  created_at: string;
  updated_at?: string;
};

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
  close_time?: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
};

export type PositionSide = "long" | "short";

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

export type TradeSide = "buy" | "sell";

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

export type KillSwitchRequest = {
  engaged: boolean;
  reason: string;
};

export type KillSwitchStatus = {
  engaged: boolean;
  reason?: string | null;
  updated_at: string;
  updated_by?: string | null;
};

export type AlertSeverity = "info" | "warning" | "critical";

export type Alert = {
  id: string;
  account_id?: string | null;
  severity: AlertSeverity;
  code: string;
  message: string;
  acknowledged: boolean;
  created_at: string;
  acknowledged_at?: string | null;
};
