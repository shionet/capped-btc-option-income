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
      message.error("请先从推荐页选择策略。");
      return;
    }
    const values = await form.validateFields();
    const data = await runRiskCheck(values.accountEquity, candidate);
    setResult(data.result);
  };

  return (
    <>
      <Typography.Title level={3}>风控检查</Typography.Title>
      <Card style={{ marginBottom: 16 }}>
        <Form form={form} layout="inline" initialValues={{ accountEquity: 100000 }}>
          <Form.Item
            label="账户资金"
            name="accountEquity"
            rules={[{ required: true, message: "请输入账户资金" }]}
          >
            <InputNumber min={1} style={{ width: 200 }} />
          </Form.Item>
          <Form.Item>
            <Button type="primary" onClick={onSubmit}>执行检查</Button>
          </Form.Item>
        </Form>
      </Card>
      <RiskResultCard result={result} />
    </>
  );
}
