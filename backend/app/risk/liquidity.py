from app.domain.models import SpreadCandidate


def check_liquidity(
    candidate: SpreadCandidate,
    *,
    max_bid_ask_spread_ratio: float,
    min_bid_price: float,
) -> tuple[bool, str]:
    short_quote = candidate.short_leg.quote
    long_quote = candidate.long_leg.quote
    if short_quote.bid < min_bid_price:
        return False, f"Short leg bid too low: {short_quote.bid:.4f} < {min_bid_price:.4f}"
    if short_quote.bid_ask_spread_ratio > max_bid_ask_spread_ratio:
        return (
            False,
            f"Short leg spread too wide: {short_quote.bid_ask_spread_ratio:.3f} > {max_bid_ask_spread_ratio:.3f}",
        )
    if long_quote.bid_ask_spread_ratio > max_bid_ask_spread_ratio:
        return (
            False,
            f"Long leg spread too wide: {long_quote.bid_ask_spread_ratio:.3f} > {max_bid_ask_spread_ratio:.3f}",
        )
    return True, "Liquidity check passed."
