import { Button, Card, Popconfirm, Space, Table, Tag, Typography } from "antd";
import type { ColumnsType } from "antd/es/table";
import { useEffect, useState } from "react";
import { closePosition, fetchPositions } from "../api/positions";
import { PositionItem } from "../types/domain";

export default function PositionsPage() {
  const [rows, setRows] = useState<PositionItem[]>([]);

  const load = () => {
    fetchPositions().then((res) => setRows(res.items || []));
  };

  useEffect(() => {
    load();
  }, []);

  const columns: ColumnsType<PositionItem> = [
    { title: "Position ID", dataIndex: "position_id", width: 180 },
    { title: "Strategy", dataIndex: "strategy_type" },
    { title: "Status", dataIndex: "status", render: (v: string) => <Tag color={v === "open" ? "green" : "blue"}>{v}</Tag> },
    { title: "Unrealized PnL (USD)", dataIndex: "unrealized_pnl", render: (v: number) => v.toFixed(2) },
    { title: "Risk Exposure (USD)", dataIndex: "max_loss", render: (v: number) => v.toFixed(2) },
    { title: "Margin (USD)", dataIndex: "margin_used", render: (v: number) => v.toFixed(2) },
    {
      title: "Action",
      render: (_, row) => (
        <Space>
          <Popconfirm title="Close this position?" onConfirm={() => closePosition(row.position_id).then(load)}>
            <Button size="small" danger>Close</Button>
          </Popconfirm>
        </Space>
      )
    }
  ];

  return (
    <>
      <Typography.Title level={3}>Positions</Typography.Title>
      <Card>
        <Table rowKey="position_id" columns={columns} dataSource={rows} pagination={{ pageSize: 10 }} />
      </Card>
    </>
  );
}
