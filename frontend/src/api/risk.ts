import { apiClient } from "./client";
import { RiskCheckResult, SpreadCandidate } from "../types/domain";

export async function runRiskCheck(accountEquity: number, candidate: SpreadCandidate) {
  const { data } = await apiClient.post<{ ok: boolean; result: RiskCheckResult }>("/api/risk/check", {
    account_equity: accountEquity,
    candidate,
    daily_risk_exposure: 0,
    daily_realized_pnl: 0
  });
  return data;
}
