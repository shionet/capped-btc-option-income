import { Card, Col, Row, Spin, Statistic, Tag, Typography } from "antd";
import { useEffect, useMemo, useState } from "react";
import { fetchAccountSummary } from "../api/account";
import { fetchBtcMarket, fetchStreamStatus } from "../api/market";
import { fetchPnlSummary } from "../api/pnl";
import { fetchTradingMode } from "../api/trading";
import { ModeBanner } from "../components/ModeBanner";
import { StatusBar } from "../components/StatusBar";

type DashboardData = {
  market: Awaited<ReturnType<typeof fetchBtcMarket>>;
  account: Awaited<ReturnType<typeof fetchAccountSummary>>;
  stream: Awaited<ReturnType<typeof fetchStreamStatus>>;
  pnl: Awaited<ReturnType<typeof fetchPnlSummary>>;
  mode: Awaited<ReturnType<typeof fetchTradingMode>>;
};

export default function DashboardPage() {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<DashboardData | null>(null);

  useEffect(() => {
    Promise.all([fetchBtcMarket(), fetchAccountSummary(), fetchStreamStatus(), fetchPnlSummary(), fetchTradingMode()])
      .then(([market, account, stream, pnl, mode]) => setData({ market, account, stream, pnl, mode }))
      .finally(() => setLoading(false));
  }, []);

  const streamConnected = useMemo(() => {
    return data?.stream.data.ws_connected && data?.stream.data.exchange_connected;
  }, [data]);

  if (loading) {
    return <Spin />;
  }

  return (
    <>
      <Typography.Title level={3}>Realtime Dashboard</Typography.Title>
      <ModeBanner />
      <StatusBar
        systemStatus={data?.market.system_status ?? "unknown"}
        ivStatus={data?.market.iv_status_proxy ?? null}
        mode={data?.mode.data.mode}
      />

      <Row gutter={16} style={{ marginTop: 16 }}>
        <Col span={8}>
          <Card>
            <Statistic title="BTC Price (USD)" value={data?.market.price ?? 0} precision={2} />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic title="IV Proxy" value={data?.market.iv_status_proxy ?? 0} precision={3} />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic title="Account Equity (USD)" value={Number(data?.account.data.total_account_asset ?? 0)} precision={2} />
          </Card>
        </Col>
      </Row>

      <Row gutter={16} style={{ marginTop: 16 }}>
        <Col span={6}>
          <Card>
            <Statistic title="Available Balance (USD)" value={Number(data?.account.data.available_balance ?? 0)} precision={2} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="Today PnL (USD)" value={Number(data?.pnl.data.today_pnl ?? 0)} precision={2} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="Total Risk Exposure (USD)" value={Number(data?.account.data.risk_exposure ?? 0)} precision={2} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="Open Positions" value={Number(data?.account.data.positions_count ?? 0)} />
          </Card>
        </Col>
      </Row>

      <Card style={{ marginTop: 16 }} title="System State">
        <Typography.Paragraph>
          Trading Mode: <Tag color={data?.mode.data.mode === "LIVE_TRADING" ? "red" : "blue"}>{data?.mode.data.mode}</Tag>
        </Typography.Paragraph>
        <Typography.Paragraph>
          Config Version: <Tag>{data?.mode.data.execution_config_version ?? "-"}</Tag>
        </Typography.Paragraph>
        <Typography.Paragraph>
          Market Stream: <Tag color={streamConnected ? "green" : "orange"}>{streamConnected ? "connected" : "degraded"}</Tag>
        </Typography.Paragraph>
      </Card>
    </>
  );
}
