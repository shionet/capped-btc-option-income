import { apiClient } from "./client";

export async function fetchAuditEvents(limit = 100) {
  const { data } = await apiClient.get<{ ok: boolean; count: number; items: Array<Record<string, unknown>> }>("/api/audit/events", {
    params: { limit }
  });
  return data;
}

export async function fetchAuditExecutions(limit = 100) {
  const { data } = await apiClient.get<{ ok: boolean; count: number; items: Array<Record<string, unknown>> }>("/api/audit/executions", {
    params: { limit }
  });
  return data;
}

export async function fetchAuditRiskBlocks(limit = 100) {
  const { data } = await apiClient.get<{ ok: boolean; count: number; items: Array<Record<string, unknown>> }>("/api/audit/risk-blocks", {
    params: { limit }
  });
  return data;
}

export async function fetchAuditErrors(limit = 100) {
  const { data } = await apiClient.get<{ ok: boolean; count: number; items: Array<Record<string, unknown>> }>("/api/audit/errors", {
    params: { limit }
  });
  return data;
}
