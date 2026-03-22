import { Navigate, Route, Routes } from "react-router-dom";
import DashboardPage from "../pages/DashboardPage";
import ExecutionPreviewPage from "../pages/ExecutionPreviewPage";
import RecommendationsPage from "../pages/RecommendationsPage";
import RiskCheckPage from "../pages/RiskCheckPage";
import StrategyDetailPage from "../pages/StrategyDetailPage";

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<DashboardPage />} />
      <Route path="/recommendations" element={<RecommendationsPage />} />
      <Route path="/strategies/:id" element={<StrategyDetailPage />} />
      <Route path="/risk-check" element={<RiskCheckPage />} />
      <Route path="/execution-preview" element={<ExecutionPreviewPage />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
