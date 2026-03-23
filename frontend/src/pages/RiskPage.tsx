import { Card, List, Tag, Typography } from "antd";
import { useEffect, useState } from "react";
import { fetchAccountRisk } from "../api/account";
import { fetchAuditRiskBlocks } from "../api/audit";

export default function RiskPage() {
  const [risk, setRisk] = useState<Record<string, unknown> | null>(null);
  const [blocks, setBlocks] = useState<Array<Record<string, unknown>>>([]);

  useEffect(() => {
    fetchAccountRisk().then((res) => setRisk(res.data));
    fetchAuditRiskBlocks(50).then((res) => setBlocks(res.items || []));
  }, []);

  return (
    <>
      <Typography.Title level={3}>Risk Control</Typography.Title>
      <Card title="Current Risk State">
        <Typography.Paragraph>
          Risk Utilization: <Tag color={Number(risk?.risk_utilization ?? 0) > 0.8 ? "red" : "green"}>{Number(risk?.risk_utilization ?? 0).toFixed(3)}</Tag>
        </Typography.Paragraph>
        <Typography.Paragraph>
          Open Allowed: <Tag color={risk?.is_open_allowed ? "green" : "red"}>{String(risk?.is_open_allowed ?? false)}</Tag>
        </Typography.Paragraph>
      </Card>
      <Card title="Risk Block Records" style={{ marginTop: 16 }}>
        <List
          dataSource={blocks}
          renderItem={(item) => (
            <List.Item>
              <div>
                <div><strong>{String(item.strategy_id ?? "-")}</strong></div>
                <div>{JSON.stringify(item.reasons ?? [])}</div>
              </div>
            </List.Item>
          )}
        />
      </Card>
    </>
  );
}
