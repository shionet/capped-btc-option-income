import { apiClient } from "./client";
import { TradingMode, TradingModeState } from "../types/domain";

export async function fetchTradingMode() {
  const { data } = await apiClient.get<{ ok: boolean; data: TradingModeState }>("/api/trading/mode");
  return data;
}

export async function updateTradingMode(mode: TradingMode) {
  const { data } = await apiClient.put<{ ok: boolean; data: TradingModeState }>("/api/trading/mode", {
    mode,
    actor: "web-user"
  });
  return data;
}

export async function fetchExecutionMonitor() {
  const { data } = await apiClient.get<{ ok: boolean; data: Record<string, unknown> }>("/api/trading/execution/monitor");
  return data;
}

export async function createExecutionPlan(strategyId: string, mode: TradingMode) {
  const { data } = await apiClient.post<{ ok: boolean; data: Record<string, unknown> }>("/api/trading/execution/plans", {
    strategy_id: strategyId,
    mode,
    quantity: 1,
    max_slippage: 0.003,
    max_retries: 2,
    timeout_seconds: 20,
    fallback_market: false,
    actor: "web-user",
    payload: {}
  });
  return data;
}

export async function confirmExecutionPlan(planId: string) {
  const { data } = await apiClient.post<{ ok: boolean; data: Record<string, unknown> }>(`/api/trading/execution/plans/${planId}/confirm`);
  return data;
}
