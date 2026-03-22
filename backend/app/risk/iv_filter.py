from app.domain.models import SpreadCandidate


def check_iv_threshold(candidate: SpreadCandidate, min_iv: float) -> tuple[bool, str]:
    # Temporary implementation:
    # use mark IV average as ATM IV proxy until we build IV history + percentile.
    if candidate.iv_proxy is None:
        return False, "IV unavailable (temporary rule blocks unknown IV)."
    if candidate.iv_proxy < min_iv:
        return False, f"IV too low: {candidate.iv_proxy:.3f} < {min_iv:.3f}"
    return True, "IV check passed."
