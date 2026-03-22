import { Card, Descriptions, Typography } from "antd";
import { STORAGE_KEY } from "./RecommendationsPage";
import { SpreadCandidate } from "../types/domain";

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

export default function StrategyDetailPage() {
  const candidate = loadCandidate();
  if (!candidate) {
    return <Card>未找到策略数据，请先在推荐页选择一个候选策略。</Card>;
  }

  return (
    <>
      <Typography.Title level={3}>策略详情</Typography.Title>
      <Card title="结构摘要">
        <Descriptions column={2}>
          <Descriptions.Item label="策略">{candidate.strategy_type}</Descriptions.Item>
          <Descriptions.Item label="到期日">{candidate.expiry}</Descriptions.Item>
          <Descriptions.Item label="净权利金">{candidate.net_premium.toFixed(2)}</Descriptions.Item>
          <Descriptions.Item label="最大亏损">{candidate.max_loss.toFixed(2)}</Descriptions.Item>
          <Descriptions.Item label="收益风险比">{candidate.reward_risk_ratio.toFixed(3)}</Descriptions.Item>
          <Descriptions.Item label="距离现价%">
            {candidate.distance_to_spot_pct.toFixed(2)}
          </Descriptions.Item>
        </Descriptions>
      </Card>
      <Card style={{ marginTop: 16 }} title="腿信息">
        <Descriptions column={1}>
          <Descriptions.Item label="卖腿">
            {candidate.short_leg.quote.contract.symbol} @ {candidate.short_leg.price}
          </Descriptions.Item>
          <Descriptions.Item label="买腿">
            {candidate.long_leg.quote.contract.symbol} @ {candidate.long_leg.price}
          </Descriptions.Item>
        </Descriptions>
      </Card>
    </>
  );
}
