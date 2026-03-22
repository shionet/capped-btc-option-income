import { Button, Card, List, Typography, message } from "antd";
import { useState } from "react";
import { runExecutionPreview } from "../api/execution";
import { ExecutionPreview, SpreadCandidate } from "../types/domain";
import { STORAGE_KEY } from "./RecommendationsPage";


function loadCandidate(): SpreadCandidate | null {
  const raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) {
    return null;
  }
  try {
    return JSON.parse(raw) as SpreadCandidate;
  } catch {
    return null;
  }
}

export default function ExecutionPreviewPage() {
  const [preview, setPreview] = useState<ExecutionPreview | null>(null);
  const candidate = loadCandidate();

  const onRun = async () => {
    if (!candidate) {
      message.error("请先从推荐页选择策略。");
      return;
    }
    const data = await runExecutionPreview(candidate, 100000);
    setPreview(data.preview);
  };

  return (
    <>
      <Typography.Title level={3}>执行预演</Typography.Title>
      <Card style={{ marginBottom: 16 }}>
        <Typography.Paragraph>
          当前为 dry-run 模式，不会真实下单。
        </Typography.Paragraph>
        <Button type="primary" onClick={onRun}>生成执行计划</Button>
      </Card>
      <Card title="拟下单明细">
        <List
          dataSource={preview?.orders ?? []}
          renderItem={(item) => (
            <List.Item>
              {item.side} {item.symbol} qty={item.quantity} price={item.price} ({item.note})
            </List.Item>
          )}
        />
        <Typography.Paragraph style={{ marginTop: 12 }}>
          预估最大风险: {preview?.max_risk ?? 0}
        </Typography.Paragraph>
      </Card>
    </>
  );
}
