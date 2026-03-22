import { apiClient } from "./client";
import { SpreadCandidate } from "../types/domain";

interface RecommendationResponse {
  ok: boolean;
  strategy_type: string;
  count: number;
  items: SpreadCandidate[];
}

export async function fetchBullPutRecommendations() {
  const { data } = await apiClient.get<RecommendationResponse>(
    "/api/strategies/bull-put-spreads/recommendations",
    { params: { exchange: "binance", limit: 30 } }
  );
  return data;
}

export async function fetchBearCallRecommendations() {
  const { data } = await apiClient.get<RecommendationResponse>(
    "/api/strategies/bear-call-spreads/recommendations",
    { params: { exchange: "binance", limit: 30 } }
  );
  return data;
}
