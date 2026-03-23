import { Alert, Space, Tag } from "antd";

interface Props {
  systemStatus: string;
  ivStatus: number | null;
  mode?: string;
}

export function StatusBar({ systemStatus, ivStatus, mode }: Props) {
  return (
    <Alert
      type="info"
      showIcon
      message={
        <Space size={16}>
          <span>System: <Tag color={systemStatus === "running" ? "green" : "orange"}>{systemStatus}</Tag></span>
          <span>IV Proxy: <Tag color="blue">{ivStatus ? ivStatus.toFixed(3) : "N/A"}</Tag></span>
          <span>Mode: <Tag color={mode === "LIVE_TRADING" ? "red" : mode === "SEMI_AUTO" ? "orange" : "gold"}>{mode ?? "DRY_RUN"}</Tag></span>
        </Space>
      }
    />
  );
}
