export type StrategyType = "bull_put_spread" | "bear_call_spread" | "iron_condor";
export type TradingMode = "DRY_RUN" | "SEMI_AUTO" | "LIVE_TRADING";
export type PositionStatus = "opening" | "open" | "closing" | "closed" | "error";

export interface OptionContract {
  symbol: string;
  underlying: string;
  expiry: string;
  strike: number;
  option_type: "put" | "call";
}

export interface OptionQuote {
  contract: OptionContract;
  bid: number;
  ask: number;
  mark?: number | null;
  iv?: number | null;
}

export interface OptionLeg {
  action: "buy" | "sell";
  quote: OptionQuote;
  quantity: number;
  price: number;
}

export interface SpreadCandidate {
  id: string;
  strategy_type: StrategyType;
  expiry: string;
  short_leg: OptionLeg;
  long_leg: OptionLeg;
  net_premium: number;
  max_profit: number;
  max_loss: number;
  reward_risk_ratio: number;
  distance_to_spot_pct: number;
  days_to_expiry: number;
  iv_proxy?: number | null;
  score: number;
  max_trade_risk?: number;
  max_position_size?: number;
  position_size_allowed?: boolean;
}

export interface RiskCheckResult {
  allowed: boolean;
  reasons: string[];
  checks: Record<string, boolean>;
  risk_metrics: Record<string, number>;
}

export interface ExecutionPreview {
  mode: TradingMode;
  strategy_type: StrategyType;
  orders: Array<{
    symbol: string;
    side: string;
    quantity: number;
    price: number;
    note: string;
  }>;
  estimated_fees: number;
  max_risk: number;
  risk_check: RiskCheckResult;
  note: string;
}

export interface TradingModeState {
  mode: TradingMode;
  live_trading_enabled: boolean;
  execution_config_version: number;
  updated_at?: string | null;
}

export interface PositionItem {
  position_id: string;
  strategy_type: string;
  underlying: string;
  exchange: string;
  opened_at?: string | null;
  closed_at?: string | null;
  expiry?: string | null;
  quantity: number;
  net_credit_open: number;
  current_value: number;
  unrealized_pnl: number;
  realized_pnl: number;
  max_profit: number;
  max_loss: number;
  risk_utilization: number;
  margin_used: number;
  status: PositionStatus;
}

export interface PnlSummary {
  realized_pnl: number;
  unrealized_pnl: number;
  today_pnl: number;
  week_pnl: number;
  month_pnl: number;
  open_positions: number;
  closed_positions: number;
}
