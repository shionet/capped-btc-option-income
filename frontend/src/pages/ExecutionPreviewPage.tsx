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
      message.error("Please select a strategy first.");
      return;
    }
    const data = await runExecutionPreview(candidate, 100000);
    setPreview(data.preview);
  };

  return (
    <>
      <Typography.Title level={3}>Execution Preview</Typography.Title>
      <Card style={{ marginBottom: 16 }}>
        <Typography.Paragraph>Execution preview only. This action does not place real orders.</Typography.Paragraph>
        <Button type="primary" onClick={onRun}>Generate Plan</Button>
      </Card>
      <Card title="Orders">
        <List
          dataSource={preview?.orders ?? []}
          renderItem={(item) => (
            <List.Item>
              {item.side} {item.symbol} qty={item.quantity} price={item.price} ({item.note})
            </List.Item>
          )}
        />
        <Typography.Paragraph style={{ marginTop: 12 }}>Estimated Max Risk: {preview?.max_risk ?? 0}</Typography.Paragraph>
      </Card>
    </>
  );
}
