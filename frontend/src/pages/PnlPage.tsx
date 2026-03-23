import { Card, Col, Row, Statistic, Table, Typography } from "antd";
import { useEffect, useState } from "react";
import { fetchPnlByStrategy, fetchPnlHistory, fetchPnlSummary } from "../api/pnl";
import { PnlSummary } from "../types/domain";

export default function PnlPage() {
  const [summary, setSummary] = useState<PnlSummary | null>(null);
  const [history, setHistory] = useState<Array<Record<string, unknown>>>([]);
  const [byStrategy, setByStrategy] = useState<Array<Record<string, unknown>>>([]);

  useEffect(() => {
    fetchPnlSummary().then((res) => setSummary(res.data));
    fetchPnlHistory().then((res) => setHistory(res.items || []));
    fetchPnlByStrategy().then((res) => setByStrategy(res.items || []));
  }, []);

  return (
    <>
      <Typography.Title level={3}>PnL Analytics</Typography.Title>
      <Row gutter={16}>
        <Col span={8}><Card><Statistic title="Realized PnL (USD)" value={summary?.realized_pnl ?? 0} precision={2} /></Card></Col>
        <Col span={8}><Card><Statistic title="Unrealized PnL (USD)" value={summary?.unrealized_pnl ?? 0} precision={2} /></Card></Col>
        <Col span={8}><Card><Statistic title="Today PnL (USD)" value={summary?.today_pnl ?? 0} precision={2} /></Card></Col>
      </Row>
      <Card style={{ marginTop: 16 }} title="Daily PnL History">
        <Table
          rowKey={(row) => String(row.date)}
          dataSource={history}
          columns={[
            { title: "Date", dataIndex: "date" },
            { title: "Total PnL", dataIndex: "total_pnl" },
            { title: "Equity", dataIndex: "equity" },
            { title: "Drawdown", dataIndex: "drawdown" }
          ]}
          pagination={{ pageSize: 8 }}
        />
      </Card>
      <Card style={{ marginTop: 16 }} title="PnL by Strategy">
        <Table
          rowKey={(row) => String(row.strategy_type)}
          dataSource={byStrategy}
          columns={[
            { title: "Strategy", dataIndex: "strategy_type" },
            { title: "Realized", dataIndex: "realized_pnl" },
            { title: "Unrealized", dataIndex: "unrealized_pnl" },
            { title: "Win Rate", dataIndex: "win_rate" }
          ]}
          pagination={false}
        />
      </Card>
    </>
  );
}
