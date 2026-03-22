export type StrategyType = "bull_put_spread" | "bear_call_spread" | "iron_condor";

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
}

export interface RiskCheckResult {
  allowed: boolean;
  reasons: string[];
  checks: Record<string, boolean>;
  risk_metrics: Record<string, number>;
}

export interface ExecutionPreview {
  mode: "dry_run" | "live";
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
