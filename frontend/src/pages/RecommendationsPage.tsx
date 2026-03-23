import { Alert, Space, Spin, Typography } from "antd";
import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { fetchBearCallRecommendations, fetchBullPutRecommendations } from "../api/strategies";
import { RecommendationTable } from "../components/RecommendationTable";
import { SpreadCandidate } from "../types/domain";

export const STORAGE_KEY = "selected_candidate";

export default function RecommendationsPage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [bull, setBull] = useState<SpreadCandidate[]>([]);
  const [bear, setBear] = useState<SpreadCandidate[]>([]);
  const navigate = useNavigate();

  useEffect(() => {
    Promise.all([fetchBullPutRecommendations(), fetchBearCallRecommendations()])
      .then(([b1, b2]) => {
        setBull(b1.items || []);
        setBear(b2.items || []);
      })
      .catch((e) => setError(String(e)))
      .finally(() => setLoading(false));
  }, []);

  const allRows = useMemo(() => [...bull, ...bear], [bull, bear]);

  const storeCandidate = (candidate: SpreadCandidate) => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(candidate));
  };

  if (loading) {
    return <Spin />;
  }

  return (
    <>
      <Typography.Title level={3}>Strategy Recommendations</Typography.Title>
      {error ? <Alert type="error" message={error} /> : null}
      <Space direction="vertical" style={{ width: "100%" }} size={16}>
        <RecommendationTable
          data={allRows}
          onDetail={(candidate) => {
            storeCandidate(candidate);
            navigate(`/strategies/${encodeURIComponent(candidate.id)}`);
          }}
          onRisk={(candidate) => {
            storeCandidate(candidate);
            navigate("/risk-check");
          }}
          onPreview={(candidate) => {
            storeCandidate(candidate);
            navigate("/execution-preview");
          }}
        />
      </Space>
    </>
  );
}
