import { Card, List, Typography } from "antd";
import { useEffect, useState } from "react";
import { fetchExecutionMonitor } from "../api/trading";

export default function ExecutionMonitorPage() {
  const [data, setData] = useState<Record<string, unknown> | null>(null);

  useEffect(() => {
    fetchExecutionMonitor().then((res) => setData(res.data));
  }, []);

  const plans = (data?.recent_plans as Array<Record<string, unknown>> | undefined) ?? [];
  const orders = (data?.recent_orders as Array<Record<string, unknown>> | undefined) ?? [];

  return (
    <>
      <Typography.Title level={3}>Execution Monitor</Typography.Title>
      <Card title="Recent Plans">
        <List
          dataSource={plans}
          renderItem={(item) => (
            <List.Item>
              {String(item.plan_id)} | {String(item.mode)} | {String(item.status)}
            </List.Item>
          )}
        />
      </Card>
      <Card title="Recent Orders" style={{ marginTop: 16 }}>
        <List
          dataSource={orders}
          renderItem={(item) => (
            <List.Item>
              {String(item.order_id)} | {String(item.symbol)} | {String(item.status)}
            </List.Item>
          )}
        />
      </Card>
    </>
  );
}
