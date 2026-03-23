import { Button, Card, Form, InputNumber, Typography, message } from "antd";
import { useState } from "react";
import { runRiskCheck } from "../api/risk";
import { RiskResultCard } from "../components/RiskResultCard";
import { RiskCheckResult, SpreadCandidate } from "../types/domain";
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

export default function RiskCheckPage() {
  const [result, setResult] = useState<RiskCheckResult | null>(null);
  const candidate = loadCandidate();
  const [form] = Form.useForm<{ accountEquity: number }>();

  const onSubmit = async () => {
    if (!candidate) {
      message.error("Please select a strategy first.");
      return;
    }
    const values = await form.validateFields();
    const data = await runRiskCheck(values.accountEquity, candidate);
    setResult(data.result);
  };

  return (
    <>
      <Typography.Title level={3}>Risk Check</Typography.Title>
      <Card style={{ marginBottom: 16 }}>
        <Form form={form} layout="inline" initialValues={{ accountEquity: 100000 }}>
          <Form.Item label="Account Equity" name="accountEquity" rules={[{ required: true, message: "Input account equity" }]}> 
            <InputNumber min={1} style={{ width: 200 }} />
          </Form.Item>
          <Form.Item>
            <Button type="primary" onClick={onSubmit}>Run Check</Button>
          </Form.Item>
        </Form>
      </Card>
      <RiskResultCard result={result} />
    </>
  );
}
