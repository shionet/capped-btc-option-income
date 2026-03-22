import { Alert, Space, Tag } from "antd";

interface Props {
  systemStatus: string;
  ivStatus: number | null;
}

export function StatusBar({ systemStatus, ivStatus }: Props) {
  return (
    <Alert
      type="info"
      showIcon
      message={
        <Space size={16}>
          <span>System: <Tag color={systemStatus === "running" ? "green" : "orange"}>{systemStatus}</Tag></span>
          <span>IV Proxy: <Tag color="blue">{ivStatus ? ivStatus.toFixed(3) : "N/A"}</Tag></span>
          <span>Mode: <Tag color="gold">Dry-run</Tag></span>
        </Space>
      }
    />
  );
}
