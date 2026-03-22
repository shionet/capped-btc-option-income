import { Card, Col, Row, Spin, Statistic, Typography } from "antd";
import { useEffect, useState } from "react";
import { fetchBtcMarket } from "../api/market";
import { StatusBar } from "../components/StatusBar";

export default function DashboardPage() {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<Awaited<ReturnType<typeof fetchBtcMarket>> | null>(null);

  useEffect(() => {
    fetchBtcMarket()
      .then(setData)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <Spin />;
  }

  return (
    <>
      <Typography.Title level={3}>Dashboard</Typography.Title>
      <StatusBar systemStatus={data?.system_status ?? "unknown"} ivStatus={data?.iv_status_proxy ?? null} />
      <Row gutter={16} style={{ marginTop: 16 }}>
        <Col span={8}>
          <Card><Statistic title="BTC 价格" value={data?.price ?? 0} precision={2} /></Card>
        </Col>
        <Col span={8}>
          <Card><Statistic title="IV Proxy" value={data?.iv_status_proxy ?? 0} precision={3} /></Card>
        </Col>
        <Col span={8}>
          <Card><Statistic title="系统状态" value={data?.system_status ?? "unknown"} /></Card>
        </Col>
      </Row>
      <Card style={{ marginTop: 16 }} title="数据更新时间">
        {data?.timestamp ?? "-"}
      </Card>
    </>
  );
}
