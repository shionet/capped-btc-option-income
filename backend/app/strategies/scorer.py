from app.domain.models import SpreadCandidate


def score_candidate(candidate: SpreadCandidate) -> float:
    # Heuristic score for MVP:
    # higher reward/risk and safer distance to spot get better score.
    rr_score = min(candidate.reward_risk_ratio, 5.0) * 20
    distance_score = min(candidate.distance_to_spot_pct, 10.0) * 3
    dte_penalty = 8 if candidate.days_to_expiry == 0 else 0
    loss_penalty = min(candidate.max_loss / max(candidate.max_profit, 1e-9), 20)
    return max(rr_score + distance_score - dte_penalty - loss_penalty, 0)
