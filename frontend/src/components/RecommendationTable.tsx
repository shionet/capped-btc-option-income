import { Button, Space, Table, Tag } from "antd";
import type { ColumnsType } from "antd/es/table";
import { SpreadCandidate } from "../types/domain";

interface Props {
  data: SpreadCandidate[];
  onDetail: (candidate: SpreadCandidate) => void;
  onRisk: (candidate: SpreadCandidate) => void;
  onPreview: (candidate: SpreadCandidate) => void;
}

export function RecommendationTable({ data, onDetail, onRisk, onPreview }: Props) {
  const columns: ColumnsType<SpreadCandidate> = [
    { title: "Strategy", dataIndex: "strategy_type", render: (v: string) => <Tag>{v}</Tag> },
    { title: "Short Leg", render: (_, row) => row.short_leg.quote.contract.symbol },
    { title: "Long Leg", render: (_, row) => row.long_leg.quote.contract.symbol },
    { title: "Expiry", dataIndex: "expiry" },
    { title: "Net Premium", dataIndex: "net_premium", render: (v: number) => v.toFixed(2) },
    { title: "Max Profit", dataIndex: "max_profit", render: (v: number) => v.toFixed(2) },
    { title: "Max Loss", dataIndex: "max_loss", render: (v: number) => v.toFixed(2) },
    { title: "R/R", dataIndex: "reward_risk_ratio", render: (v: number) => v.toFixed(3) },
    { title: "IV", dataIndex: "iv_proxy", render: (v?: number | null) => (v == null ? "N/A" : v.toFixed(3)) },
    { title: "Distance %", dataIndex: "distance_to_spot_pct", render: (v: number) => v.toFixed(2) },
    {
      title: "Action",
      render: (_, row) => (
        <Space>
          <Button size="small" onClick={() => onDetail(row)}>Detail</Button>
          <Button size="small" onClick={() => onRisk(row)}>Risk</Button>
          <Button size="small" type="primary" onClick={() => onPreview(row)}>Preview</Button>
        </Space>
      )
    }
  ];

  return <Table rowKey="id" dataSource={data} columns={columns} pagination={{ pageSize: 10 }} />;
}
