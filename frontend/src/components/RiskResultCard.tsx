import { Card, List, Tag } from "antd";
import { RiskCheckResult } from "../types/domain";

interface Props {
  result?: RiskCheckResult | null;
}

export function RiskResultCard({ result }: Props) {
  if (!result) {
    return <Card title="风控结果">暂无数据</Card>;
  }
  return (
    <Card
      title="风控结果"
      extra={<Tag color={result.allowed ? "green" : "red"}>{result.allowed ? "允许开仓" : "禁止开仓"}</Tag>}
    >
      <List
        size="small"
        header="原因"
        dataSource={result.reasons}
        renderItem={(item) => <List.Item>{item}</List.Item>}
      />
    </Card>
  );
}
