import { apiClient } from "./client";
import { ExecutionPreview, SpreadCandidate } from "../types/domain";

export async function runExecutionPreview(candidate: SpreadCandidate, accountEquity: number) {
  const { data } = await apiClient.post<{ ok: boolean; preview: ExecutionPreview }>("/api/execution/preview", {
    mode: "dry_run",
    quantity: 1,
    candidate,
    account_equity: accountEquity,
    daily_risk_exposure: 0,
    daily_realized_pnl: 0
  });
  return data;
}
