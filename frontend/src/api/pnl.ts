import { apiClient } from "./client";
import { PnlSummary } from "../types/domain";

export async function fetchPnlSummary() {
  const { data } = await apiClient.get<{ ok: boolean; data: PnlSummary }>("/api/pnl/summary");
  return data;
}

export async function fetchPnlHistory(limit = 60) {
  const { data } = await apiClient.get<{ ok: boolean; count: number; items: Array<Record<string, unknown>> }>("/api/pnl/history", {
    params: { limit }
  });
  return data;
}

export async function fetchPnlByStrategy() {
  const { data } = await apiClient.get<{ ok: boolean; count: number; items: Array<Record<string, unknown>> }>("/api/pnl/by-strategy");
  return data;
}
