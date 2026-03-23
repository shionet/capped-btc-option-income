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
    binance_exchange_info_cache_ttl_seconds: int = Field(
        default=5,
        alias="BINANCE_EXCHANGE_INFO_CACHE_TTL_SECONDS",
    )

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

    strategy_underlying: str = Field(default="BTC", alias="STRATEGY_UNDERLYING")
    strategy_allowed_exchanges: str = Field(default="binance", alias="STRATEGY_ALLOWED_EXCHANGES")
    strategy_candidate_limit: int = Field(default=30, alias="STRATEGY_CANDIDATE_LIMIT")
    strategy_allowed_dte_min: int = Field(default=0, alias="STRATEGY_ALLOWED_DTE_MIN")
    strategy_allowed_dte_max: int = Field(default=7, alias="STRATEGY_ALLOWED_DTE_MAX")

    strategy_bull_put_sell_otm_min_pct: float = Field(default=2.0, alias="STRATEGY_BPS_SELL_OTM_MIN_PCT")
    strategy_bull_put_sell_otm_max_pct: float = Field(default=5.0, alias="STRATEGY_BPS_SELL_OTM_MAX_PCT")
    strategy_bull_put_buy_wing_min_pct: float = Field(default=3.0, alias="STRATEGY_BPS_BUY_WING_MIN_PCT")
    strategy_bull_put_buy_wing_max_pct: float = Field(default=8.0, alias="STRATEGY_BPS_BUY_WING_MAX_PCT")
    strategy_bull_put_min_net_premium: float = Field(default=10.0, alias="STRATEGY_BPS_MIN_NET_PREMIUM")
    strategy_bull_put_min_reward_risk: float = Field(default=0.12, alias="STRATEGY_BPS_MIN_REWARD_RISK")
    strategy_bull_put_max_width: float = Field(default=10000.0, alias="STRATEGY_BPS_MAX_WIDTH")

    strategy_bear_call_sell_otm_min_pct: float = Field(default=2.0, alias="STRATEGY_BCS_SELL_OTM_MIN_PCT")
    strategy_bear_call_sell_otm_max_pct: float = Field(default=5.0, alias="STRATEGY_BCS_SELL_OTM_MAX_PCT")
    strategy_bear_call_buy_wing_min_pct: float = Field(default=3.0, alias="STRATEGY_BCS_BUY_WING_MIN_PCT")
    strategy_bear_call_buy_wing_max_pct: float = Field(default=8.0, alias="STRATEGY_BCS_BUY_WING_MAX_PCT")
    strategy_bear_call_min_net_premium: float = Field(default=10.0, alias="STRATEGY_BCS_MIN_NET_PREMIUM")
    strategy_bear_call_min_reward_risk: float = Field(default=0.12, alias="STRATEGY_BCS_MIN_REWARD_RISK")
    strategy_bear_call_max_width: float = Field(default=10000.0, alias="STRATEGY_BCS_MAX_WIDTH")

    iv_min: float = Field(default=0.35, alias="IV_MIN")
    iv_max: float | None = Field(default=None, alias="IV_MAX")
    iv_min_percentile: float = Field(default=0.2, alias="IV_MIN_PERCENTILE")
    iv_window_minutes: int = Field(default=240, alias="IV_WINDOW_MINUTES")
    iv_filter_enabled: bool = Field(default=True, alias="IV_FILTER_ENABLED")

    liquidity_min_bid: float = Field(default=1.0, alias="LIQUIDITY_MIN_BID")
    liquidity_min_ask_depth: float = Field(default=0.0, alias="LIQUIDITY_MIN_ASK_DEPTH")
    liquidity_max_bid_ask_spread: float = Field(default=0.35, alias="LIQUIDITY_MAX_BID_ASK_SPREAD")
    liquidity_min_activity: float = Field(default=0.0, alias="LIQUIDITY_MIN_ACTIVITY")

    risk_max_positions: int = Field(default=20, alias="RISK_MAX_POSITIONS")
    risk_max_same_direction_positions: int = Field(default=10, alias="RISK_MAX_SAME_DIRECTION_POSITIONS")
    risk_consecutive_loss_pause_threshold: int = Field(default=3, alias="RISK_CONSECUTIVE_LOSS_PAUSE_THRESHOLD")

    trading_enabled: bool = Field(default=False, alias="TRADING_ENABLED")
    trading_default_mode: str = Field(default="DRY_RUN", alias="TRADING_DEFAULT_MODE")
    execution_leg_timeout_seconds: int = Field(default=20, alias="EXECUTION_LEG_TIMEOUT_SECONDS")
    execution_max_retries: int = Field(default=2, alias="EXECUTION_MAX_RETRIES")
    execution_max_slippage: float = Field(default=0.003, alias="EXECUTION_MAX_SLIPPAGE")
    execution_market_fallback_enabled: bool = Field(default=False, alias="EXECUTION_MARKET_FALLBACK_ENABLED")

    auto_close_take_profit_pct: float = Field(default=0.8, alias="AUTO_CLOSE_TAKE_PROFIT_PCT")
    auto_close_stop_loss_pct: float = Field(default=0.5, alias="AUTO_CLOSE_STOP_LOSS_PCT")
    auto_close_before_expiry_minutes: int = Field(default=30, alias="AUTO_CLOSE_BEFORE_EXPIRY_MINUTES")
    auto_close_enabled: bool = Field(default=True, alias="AUTO_CLOSE_ENABLED")
    auto_close_alert_only: bool = Field(default=False, alias="AUTO_CLOSE_ALERT_ONLY")

    trading_live_enabled: bool = Field(default=False, alias="TRADING_LIVE_ENABLED")
    enable_live_trading: bool = Field(default=False, alias="ENABLE_LIVE_TRADING")

    refresh_market_seconds: int = Field(default=10, alias="REFRESH_MARKET_SECONDS")
    refresh_account_seconds: int = Field(default=30, alias="REFRESH_ACCOUNT_SECONDS")
    refresh_positions_seconds: int = Field(default=30, alias="REFRESH_POSITIONS_SECONDS")
    refresh_strategies_seconds: int = Field(default=30, alias="REFRESH_STRATEGIES_SECONDS")
    refresh_health_seconds: int = Field(default=60, alias="REFRESH_HEALTH_SECONDS")

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

    def allowed_exchanges_values(self) -> set[str]:
        values: set[str] = set()
        for part in self.strategy_allowed_exchanges.split(","):
            part = part.strip().lower()
            if part:
                values.add(part)
        return values or {"binance"}

    def live_trading_permitted(self) -> bool:
        return bool(self.enable_live_trading or self.trading_live_enabled)


@lru_cache
def get_settings() -> Settings:
    return Settings()
