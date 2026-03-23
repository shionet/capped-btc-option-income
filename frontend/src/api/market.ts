import { apiClient } from "./client";

export interface BtcMarketResponse {
  ok: boolean;
  exchange: string;
  symbol: string;
  price: number;
  mark_price: number;
  timestamp: string;
  iv_status_proxy: number | null;
  system_status: string;
}

export async function fetchBtcMarket() {
  const { data } = await apiClient.get<BtcMarketResponse>("/api/market/btc");
  return data;
}

export interface StreamStatusResponse {
  ok: boolean;
  data: {
    ws_connected: boolean;
    exchange_connected: boolean;
    last_quote_at?: string | null;
    last_chain_at?: string | null;
  };
}

export async function fetchStreamStatus() {
  const { data } = await apiClient.get<StreamStatusResponse>("/api/market/stream-status");
  return data;
}

export async function fetchLatestQuote() {
  const { data } = await apiClient.get<{ ok: boolean; data: { quote: Record<string, unknown>; updated_at?: string | null } }>(
    "/api/market/quotes/latest"
  );
  return data;
}

export async function fetchRealtimeChain(limit = 100) {
  const { data } = await apiClient.get<{ ok: boolean; data: { items: Array<Record<string, unknown>>; count: number; updated_at?: string | null } }>(
    "/api/options/realtime-chain",
    { params: { limit } }
  );
  return data;
}
