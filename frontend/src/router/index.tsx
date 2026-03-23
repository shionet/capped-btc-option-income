import { Navigate, Route, Routes } from "react-router-dom";
import ConfigPage from "../pages/ConfigPage";
import DashboardPage from "../pages/DashboardPage";
import ExecutionPreviewPage from "../pages/ExecutionPreviewPage";
import ExecutionMonitorPage from "../pages/ExecutionMonitorPage";
import PnlPage from "../pages/PnlPage";
import PositionsPage from "../pages/PositionsPage";
import RecommendationsPage from "../pages/RecommendationsPage";
import RiskPage from "../pages/RiskPage";
import RiskCheckPage from "../pages/RiskCheckPage";
import StrategyDetailPage from "../pages/StrategyDetailPage";

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="/dashboard" element={<DashboardPage />} />
      <Route path="/strategies" element={<RecommendationsPage />} />
      <Route path="/strategies/:id" element={<StrategyDetailPage />} />
      <Route path="/risk-check" element={<RiskCheckPage />} />
      <Route path="/execution-preview" element={<ExecutionPreviewPage />} />
      <Route path="/positions" element={<PositionsPage />} />
      <Route path="/pnl" element={<PnlPage />} />
      <Route path="/risk" element={<RiskPage />} />
      <Route path="/config" element={<ConfigPage />} />
      <Route path="/execution-monitor" element={<ExecutionMonitorPage />} />
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}
