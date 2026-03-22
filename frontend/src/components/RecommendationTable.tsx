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
    { title: "策略", dataIndex: "strategy_type", render: (v: string) => <Tag>{v}</Tag> },
    { title: "卖腿", render: (_, row) => row.short_leg.quote.contract.symbol },
    { title: "买腿", render: (_, row) => row.long_leg.quote.contract.symbol },
    { title: "到期日", dataIndex: "expiry" },
    { title: "净权利金", dataIndex: "net_premium", render: (v: number) => v.toFixed(2) },
    { title: "最大亏损", dataIndex: "max_loss", render: (v: number) => v.toFixed(2) },
    { title: "收益风险比", dataIndex: "reward_risk_ratio", render: (v: number) => v.toFixed(3) },
    { title: "距离现价%", dataIndex: "distance_to_spot_pct", render: (v: number) => v.toFixed(2) },
    {
      title: "操作",
      render: (_, row) => (
        <Space>
          <Button size="small" onClick={() => onDetail(row)}>详情</Button>
          <Button size="small" onClick={() => onRisk(row)}>风控检查</Button>
          <Button size="small" type="primary" onClick={() => onPreview(row)}>执行预演</Button>
        </Space>
      )
    }
  ];

  return <Table rowKey="id" dataSource={data} columns={columns} pagination={{ pageSize: 10 }} />;
}
