from app.domain.models import PositionSnapshot


class PortfolioService:
    def get_snapshot(self) -> PositionSnapshot:
        # TODO phase 2: pull actual exchange positions and persisted local records.
        return PositionSnapshot(
            account_id="local-mvp",
            open_positions=[],
            daily_realized_pnl=0.0,
            daily_unrealized_pnl=0.0,
            daily_risk_exposure=0.0,
        )
