import { apiClient } from "./client";
import { PositionItem } from "../types/domain";

export async function fetchPositions() {
  const { data } = await apiClient.get<{ ok: boolean; count: number; items: PositionItem[]; summary: Record<string, unknown> }>("/api/positions");
  return data;
}

export async function fetchOpenPositions() {
  const { data } = await apiClient.get<{ ok: boolean; count: number; items: PositionItem[] }>("/api/positions/open");
  return data;
}

export async function fetchClosedPositions() {
  const { data } = await apiClient.get<{ ok: boolean; count: number; items: PositionItem[] }>("/api/positions/closed");
  return data;
}

export async function fetchPositionDetail(positionId: string) {
  const { data } = await apiClient.get<{ ok: boolean; item: PositionItem & { legs: Array<Record<string, unknown>> } }>(`/api/positions/${positionId}`);
  return data;
}

export async function closePosition(positionId: string) {
  const { data } = await apiClient.post<{ ok: boolean; item: PositionItem }>(`/api/positions/${positionId}/close`);
  return data;
}
