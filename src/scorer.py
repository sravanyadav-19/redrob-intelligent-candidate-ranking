"""
Module: Final Scoring Engine
Owner: Sravan
Branch: feature/sravan-scorer
Purpose: Combine all signals into final weighted score per candidate.
         Apply hard disqualifiers. Sort and return top 100.
Input: semantic_scores.json + structured_features.json + behavioral_scores.json
       + parsed_candidates.json
Output: final ranked list (top 100)

Scoring formula:
  Final Score =
    0.35 * semantic_job_match
  + 0.25 * systems_built_score
  + 0.15 * production_ml_score
  + 0.10 * product_company_boost
  + 0.10 * behavior_score
  + 0.05 * exp_depth_score

Hard disqualifiers (score capped):
  - is_honeypot          → cap at 0.05
  - domain_mismatch      → cap at 0.10
  - consulting_only
    + skill_career_mismatch → cap at 0.15
  - not location_eligible → cap at 0.10

Tiebreak order:
  1. final_score DESC
  2. systems_built_score DESC
  3. behavior_score DESC
  4. candidate_id ASC
"""

import json
from pathlib import Path


# ── Weights ───────────────────────────────────────────────────────────────────
WEIGHTS = {
    "semantic":          0.25,
    "systems_built":     0.35,
    "production_ml":     0.15,
    "product_company":   0.10,
    "behavior":          0.10,
    "exp_depth":         0.05,
}


def normalize_semantic(raw_score: float,
                        min_score: float = 0.0,
                        max_score: float = 0.2102) -> float:
    """
    Normalize TF-IDF cosine similarity to 0-1 range.
    Max observed score from embedder run = 0.2102
    """
    if max_score <= min_score:
        return 0.0
    normalized = (raw_score - min_score) / (max_score - min_score)
    return max(0.0, min(1.0, normalized))


def compute_score(
    semantic_raw:    float,
    systems_built:   float,
    production_ml:   float,
    product_company: float,
    behavior:        float,
    exp_depth:       float,
) -> float:
    semantic_norm = normalize_semantic(semantic_raw)

    score = (
        WEIGHTS["semantic"]        * semantic_norm   +
        WEIGHTS["systems_built"]   * systems_built   +
        WEIGHTS["production_ml"]   * production_ml   +
        WEIGHTS["product_company"] * product_company +
        WEIGHTS["behavior"]        * behavior        +
        WEIGHTS["exp_depth"]       * exp_depth
    )
    return round(score, 6)


def apply_disqualifiers(
    score:              float,
    is_honeypot:        bool,
    domain_mismatch:    bool,
    consulting_only:    bool,
    skill_mismatch:     bool,
    location_eligible:  bool,
    title_chasing:      bool,
) -> float:
    """
    Apply hard caps for disqualifying conditions.
    Order matters — apply the harshest cap first.
    """
    if is_honeypot:
        return min(score, 0.05)

    if domain_mismatch:
        return min(score, 0.10)

    if not location_eligible:
        return min(score, 0.10)

    if consulting_only and skill_mismatch:
        return min(score, 0.15)

    if consulting_only:
        score = score * 0.70   # 30% penalty but not hard cap

    if title_chasing:
        score = max(0.0, score - 0.05)

    return round(score, 6)


def rank_candidates(
    parsed_list:      list,
    semantic_scores:  dict,
    features_dict:    dict,
    behavioral_dict:  dict,
    top_n:            int = 100,
) -> list:
    """
    Score all candidates and return top_n sorted by final score.
    """
    results = []

    for parsed in parsed_list:
        cid = parsed["candidate_id"]

        # Get all signals
        sem_raw  = semantic_scores.get(cid, 0.0)
        feat     = features_dict.get(cid, {})
        behav    = behavioral_dict.get(cid, {})

        systems_built   = feat.get("systems_built_score",   0.0)
        production_ml   = feat.get("production_ml_score",   0.0)
        product_company = feat.get("product_company_boost", 0.0)
        exp_depth       = feat.get("exp_depth_score",       0.0)
        behavior        = behav.get("behavior_score",        0.0)

        # Flags
        is_honeypot      = feat.get("is_honeypot",           False)
        domain_mismatch  = feat.get("domain_mismatch",       False)
        consulting_only  = feat.get("consulting_only",        False)
        skill_mismatch   = feat.get("skill_career_mismatch", False)
        location_eligible= parsed.get("location_eligible",   True)
        title_chasing    = feat.get("title_chasing",         False)

        # Compute base score
        base_score = compute_score(
            semantic_raw    = sem_raw,
            systems_built   = systems_built,
            production_ml   = production_ml,
            product_company = product_company,
            behavior        = behavior,
            exp_depth       = exp_depth,
        )

        # Apply disqualifiers
        final_score = apply_disqualifiers(
            score             = base_score,
            is_honeypot       = is_honeypot,
            domain_mismatch   = domain_mismatch,
            consulting_only   = consulting_only,
            skill_mismatch    = skill_mismatch,
            location_eligible = location_eligible,
            title_chasing     = title_chasing,
        )

        results.append({
            "candidate_id":       cid,
            "final_score":        final_score,
            "semantic_score":     round(normalize_semantic(sem_raw), 4),
            "systems_built_score":round(systems_built, 4),
            "production_ml_score":round(production_ml, 4),
            "behavior_score":     round(behavior, 4),
            "exp_depth_score":    round(exp_depth, 4),
            "is_honeypot":        is_honeypot,
            "domain_mismatch":    domain_mismatch,
            "consulting_only":    consulting_only,
            "location_eligible":  location_eligible,
        })

    # Sort: final_score DESC, systems_built DESC, behavior DESC, cid ASC
    results.sort(key=lambda x: (
        -x["final_score"],
        -x["systems_built_score"],
        -x["behavior_score"],
         x["candidate_id"],
    ))

    # Assign ranks
    for rank, r in enumerate(results[:top_n], start=1):
        r["rank"] = rank

    return results[:top_n]


def load_and_score(
    parsed_path:   str = "data/parsed_candidates.json",
    semantic_path: str = "data/semantic_scores.json",
    features_path: str = "data/structured_features.json",
    behavioral_path: str = "data/behavioral_scores.json",
    top_n:         int = 100,
) -> list:

    print("Loading all signal files...")

    with open(parsed_path,    "r", encoding="utf-8") as f:
        parsed_list = json.load(f)

    with open(semantic_path,  "r", encoding="utf-8") as f:
        semantic_scores = json.load(f)

    with open(features_path,  "r", encoding="utf-8") as f:
        features_dict = json.load(f)

    with open(behavioral_path,"r", encoding="utf-8") as f:
        behavioral_dict = json.load(f)

    print(f"Scoring {len(parsed_list)} candidates...")
    top_candidates = rank_candidates(
        parsed_list     = parsed_list,
        semantic_scores = semantic_scores,
        features_dict   = features_dict,
        behavioral_dict = behavioral_dict,
        top_n           = top_n,
    )

    print(f"\nTop 10 candidates:")
    print(f"{'Rank':<6} {'Candidate ID':<15} {'Score':<8} "
          f"{'Semantic':<10} {'Systems':<10} {'Behavior':<10}")
    print("-" * 60)
    for r in top_candidates[:10]:
        print(f"{r['rank']:<6} {r['candidate_id']:<15} "
              f"{r['final_score']:<8.4f} "
              f"{r['semantic_score']:<10.4f} "
              f"{r['systems_built_score']:<10.4f} "
              f"{r['behavior_score']:<10.4f}")

    return top_candidates


if __name__ == "__main__":
    top = load_and_score()
    print(f"\nScoring complete. Top candidate: {top[0]['candidate_id']} "
          f"with score {top[0]['final_score']}")
