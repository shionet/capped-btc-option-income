from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = Field(default="crypto-option-income", alias="APP_NAME")
    app_env: str = Field(default="dev", alias="APP_ENV")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    binance_base_url: str = Field(default="https://api.binance.com", alias="BINANCE_BASE_URL")
    binance_options_base_url: str = Field(default="https://eapi.binance.com", alias="BINANCE_OPTIONS_BASE_URL")
    binance_timeout_seconds: int = Field(default=12, alias="BINANCE_TIMEOUT_SECONDS")
    binance_recv_window: int = Field(default=5000, alias="BINANCE_RECV_WINDOW")

    binance_api_key: str | None = Field(default=None, alias="BINANCE_API_KEY")
    binance_api_secret: str | None = Field(default=None, alias="BINANCE_API_SECRET")

    risk_max_single_trade_loss_pct: float = Field(default=0.03, alias="RISK_MAX_SINGLE_TRADE_LOSS_PCT")
    risk_max_daily_exposure_pct: float = Field(default=0.15, alias="RISK_MAX_DAILY_EXPOSURE_PCT")
    risk_max_daily_loss_pct: float = Field(default=0.05, alias="RISK_MAX_DAILY_LOSS_PCT")
    risk_max_bid_ask_spread_ratio: float = Field(default=0.35, alias="RISK_MAX_BID_ASK_SPREAD_RATIO")
    risk_min_iv: float = Field(default=0.35, alias="RISK_MIN_IV")
    risk_min_bid_price: float = Field(default=1.0, alias="RISK_MIN_BID_PRICE")

    strategy_sell_otm_min_pct: float = Field(default=2.0, alias="STRATEGY_SELL_OTM_MIN_PCT")
    strategy_sell_otm_max_pct: float = Field(default=5.0, alias="STRATEGY_SELL_OTM_MAX_PCT")
    strategy_wing_width_min_pct: float = Field(default=3.0, alias="STRATEGY_WING_WIDTH_MIN_PCT")
    strategy_wing_width_max_pct: float = Field(default=8.0, alias="STRATEGY_WING_WIDTH_MAX_PCT")
    strategy_allowed_dte: str = Field(default="0,1,3", alias="STRATEGY_ALLOWED_DTE")

    trading_live_enabled: bool = Field(default=False, alias="TRADING_LIVE_ENABLED")

    def allowed_dte_values(self) -> set[int]:
        values: set[int] = set()
        for part in self.strategy_allowed_dte.split(","):
            part = part.strip()
            if not part:
                continue
            try:
                values.add(int(part))
            except ValueError:
                continue
        return values or {0, 1, 3}


@lru_cache
def get_settings() -> Settings:
    return Settings()
