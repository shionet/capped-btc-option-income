import { Card, List, Tag } from "antd";
import { RiskCheckResult } from "../types/domain";

interface Props {
  result?: RiskCheckResult | null;
}

export function RiskResultCard({ result }: Props) {
  if (!result) {
    return <Card title="Risk Result">No data</Card>;
  }
  return (
    <Card title="Risk Result" extra={<Tag color={result.allowed ? "green" : "red"}>{result.allowed ? "Allowed" : "Blocked"}</Tag>}>
      <List size="small" header="Reasons" dataSource={result.reasons} renderItem={(item) => <List.Item>{item}</List.Item>} />
    </Card>
  );
}
