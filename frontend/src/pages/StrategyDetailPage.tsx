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
    return <Card>No selected strategy found. Please select one from recommendations.</Card>;
  }

  return (
    <>
      <Typography.Title level={3}>Strategy Detail</Typography.Title>
      <Card title="Summary">
        <Descriptions column={2}>
          <Descriptions.Item label="Strategy">{candidate.strategy_type}</Descriptions.Item>
          <Descriptions.Item label="Expiry">{candidate.expiry}</Descriptions.Item>
          <Descriptions.Item label="Net Premium">{candidate.net_premium.toFixed(2)}</Descriptions.Item>
          <Descriptions.Item label="Max Loss">{candidate.max_loss.toFixed(2)}</Descriptions.Item>
          <Descriptions.Item label="Reward/Risk">{candidate.reward_risk_ratio.toFixed(3)}</Descriptions.Item>
          <Descriptions.Item label="Distance to Spot %">{candidate.distance_to_spot_pct.toFixed(2)}</Descriptions.Item>
        </Descriptions>
      </Card>
      <Card style={{ marginTop: 16 }} title="Legs">
        <Descriptions column={1}>
          <Descriptions.Item label="Short Leg">{candidate.short_leg.quote.contract.symbol} @ {candidate.short_leg.price}</Descriptions.Item>
          <Descriptions.Item label="Long Leg">{candidate.long_leg.quote.contract.symbol} @ {candidate.long_leg.price}</Descriptions.Item>
        </Descriptions>
      </Card>
    </>
  );
}
