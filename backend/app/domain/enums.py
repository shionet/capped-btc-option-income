from enum import Enum


class ExchangeName(str, Enum):
    BINANCE = "binance"
    OKX = "okx"


class OptionType(str, Enum):
    PUT = "put"
    CALL = "call"


class LegAction(str, Enum):
    BUY = "buy"
    SELL = "sell"


class StrategyType(str, Enum):
    BULL_PUT_SPREAD = "bull_put_spread"
    BEAR_CALL_SPREAD = "bear_call_spread"
    IRON_CONDOR = "iron_condor"


class RunMode(str, Enum):
    DRY_RUN = "dry_run"
    LIVE = "live"
