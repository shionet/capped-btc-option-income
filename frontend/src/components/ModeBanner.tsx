import { Alert, Tag, Typography } from "antd";
import { useEffect, useState } from "react";
import { fetchTradingMode } from "../api/trading";
import { TradingModeState } from "../types/domain";

export function ModeBanner() {
  const [state, setState] = useState<TradingModeState | null>(null);

  useEffect(() => {
    fetchTradingMode()
      .then((res) => setState(res.data))
      .catch(() => setState(null));
  }, []);

  if (!state) {
    return null;
  }

  const isLive = state.mode === "LIVE_TRADING";

  return (
    <Alert
      showIcon
      type={isLive ? "error" : state.mode === "SEMI_AUTO" ? "warning" : "info"}
      message={
        <Typography.Text>
          Current Mode: <Tag color={isLive ? "red" : state.mode === "SEMI_AUTO" ? "orange" : "blue"}>{state.mode}</Tag>
          {isLive ? " LIVE_TRADING is enabled. All operations may place real orders." : " Real orders are guarded by mode control."}
        </Typography.Text>
      }
      style={{ marginBottom: 16 }}
    />
  );
}
