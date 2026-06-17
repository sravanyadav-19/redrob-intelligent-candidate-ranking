"""
Module: Behavioral Signal Scorer
Owner: Sahitya
Branch: feature/sahitya-behavioral
Purpose: Score Redrob platform behavioral signals per candidate
Input: data/parsed_candidates.json
Output: data/behavioral_scores.json
"""

import json
from datetime import datetime
from pathlib import Path


REFERENCE_DATE = datetime(2026, 6, 17)  # today's date


def days_since(date_str: str) -> int:
    """Return days since last_active_date. Returns 999 if missing."""
    if not date_str:
        return 999
    try:
        dt = datetime.strptime(date_str.strip(), "%Y-%m-%d")
        return max(0, (REFERENCE_DATE - dt).days)
    except Exception:
        return 999


def recency_score(last_active_date: str) -> float:
    """
    How recently was the candidate active on the platform.
    Recent = high intent to be hired.
    """
    days = days_since(last_active_date)
    if days <= 7:
        return 1.00
    elif days <= 14:
        return 0.90
    elif days <= 30:
        return 0.75
    elif days <= 60:
        return 0.55
    elif days <= 90:
        return 0.35
    elif days <= 180:
        return 0.20
    elif days <= 365:
        return 0.10
    else:
        return 0.02


def notice_score(notice_days: int) -> float:
    """
    JD prefers sub-30 day notice. Can buy out up to 30 days.
    30+ day notice = progressively penalized.
    """
    if notice_days <= 0:
        return 1.00
    elif notice_days <= 30:
        return 1.00
    elif notice_days <= 60:
        return 0.80
    elif notice_days <= 90:
        return 0.60
    elif notice_days <= 120:
        return 0.40
    else:
        return 0.20


def open_to_work_score(flag: bool) -> float:
    return 1.0 if flag else 0.60


def response_rate_score(rate: float) -> float:
    """Already 0-1, just validate range."""
    return max(0.0, min(1.0, rate))


def github_score_norm(github_score: float) -> float:
    """
    Github activity 0-100 → normalize to 0-1.
    -1 means no GitHub linked → treat as 0.
    """
    if github_score < 0:
        return 0.0
    return min(github_score / 100.0, 1.0)


def profile_completeness_norm(score: float) -> float:
    """0-100 → 0-1."""
    return min(score / 100.0, 1.0)


def compute_behavior_score(parsed: dict) -> dict:
    """
    Compute all behavioral sub-scores and final behavior_score.

    Weights:
      recency          40%  — are they actively looking?
      response_rate    25%  — will they actually reply?
      open_to_work     15%  — have they signaled availability?
      notice_period    10%  — can we hire them quickly?
      github_activity   5%  — bonus for visible technical work
      profile_complete  5%  — trust signal
    """
    cid = parsed["candidate_id"]

    r_score   = recency_score(parsed.get("last_active_date", ""))
    rr_score  = response_rate_score(parsed.get("response_rate", 0.3))
    otw_score = open_to_work_score(parsed.get("open_to_work", False))
    n_score   = notice_score(parsed.get("notice_days", 60))
    gh_score  = github_score_norm(parsed.get("github_score", 0.0))
    pc_score  = profile_completeness_norm(
                    parsed.get("profile_completeness", 50.0))

    behavior_score = (
        0.40 * r_score   +
        0.25 * rr_score  +
        0.15 * otw_score +
        0.10 * n_score   +
        0.05 * gh_score  +
        0.05 * pc_score
    )

    return {
        "candidate_id":        cid,
        "recency_score":       round(r_score,   4),
        "response_rate_score": round(rr_score,  4),
        "open_to_work_score":  round(otw_score, 4),
        "notice_score":        round(n_score,   4),
        "github_score":        round(gh_score,  4),
        "profile_complete_score": round(pc_score, 4),
        "behavior_score":      round(behavior_score, 4),
        # Pass through for reasoning generator
        "last_active_date":    parsed.get("last_active_date", ""),
        "notice_days":         parsed.get("notice_days", 60),
        "open_to_work":        parsed.get("open_to_work", False),
        "willing_relocate":    parsed.get("willing_relocate", False),
        "location_eligible":   parsed.get("location_eligible", True),
    }


def score_all(parsed_path: str, output_path: str):
    parsed_path = Path(parsed_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Loading: {parsed_path}")
    with open(parsed_path, "r", encoding="utf-8") as f:
        parsed_list = json.load(f)

    print(f"Scoring behavioral signals for {len(parsed_list)} candidates...")
    scores = [compute_behavior_score(p) for p in parsed_list]

    # Stats
    active_7d  = sum(1 for s in scores if s["recency_score"] >= 1.0)
    active_30d = sum(1 for s in scores if s["recency_score"] >= 0.75)
    open_work  = sum(1 for s in scores if s["open_to_work"])
    sub_30_notice = sum(1 for s in scores
                        if s["notice_days"] <= 30)

    print(f"\nBehavioral scoring complete:")
    print(f"  Active last 7 days:   {active_7d}")
    print(f"  Active last 30 days:  {active_30d}")
    print(f"  Open to work:         {open_work}")
    print(f"  Notice <= 30 days:    {sub_30_notice}")

    # Save as dict keyed by candidate_id
    scores_dict = {s["candidate_id"]: s for s in scores}
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(scores_dict, f)

    print(f"\nSaved: {output_path}")
    return scores_dict


if __name__ == "__main__":
    score_all(
        parsed_path="data/parsed_candidates.json",
        output_path="data/behavioral_scores.json"
    )
