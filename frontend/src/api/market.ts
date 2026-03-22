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
