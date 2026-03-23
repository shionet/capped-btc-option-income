import { apiClient } from "./client";

export type ConfigDomain = "strategy" | "risk" | "execution";

export async function fetchConfig(domain: ConfigDomain) {
  const { data } = await apiClient.get<{ ok: boolean; data: Record<string, unknown> }>(`/api/config/${domain}`);
  return data;
}

export async function updateConfig(domain: ConfigDomain, payload: Record<string, unknown>, publish = true) {
  const { data } = await apiClient.put<{ ok: boolean; data: Record<string, unknown> }>(`/api/config/${domain}`, {
    payload,
    publish,
    actor: "web-user"
  });
  return data;
}
