import { apiClient } from "./client";

export async function fetchAccountSummary(refresh = false) {
  const { data } = await apiClient.get<{ ok: boolean; data: Record<string, unknown> }>("/api/account/summary", {
    params: { refresh }
  });
  return data;
}

export async function fetchAccountRisk() {
  const { data } = await apiClient.get<{ ok: boolean; data: Record<string, unknown> }>("/api/account/risk");
  return data;
}

export async function fetchAccountPositions() {
  const { data } = await apiClient.get<{ ok: boolean; data: Record<string, unknown> }>("/api/account/positions");
  return data;
}

export async function fetchAccountPnl() {
  const { data } = await apiClient.get<{ ok: boolean; data: Record<string, unknown> }>("/api/account/pnl");
  return data;
}

export async function fetchAccountMargin() {
  const { data } = await apiClient.get<{ ok: boolean; data: Record<string, unknown> }>("/api/account/margin");
  return data;
}
