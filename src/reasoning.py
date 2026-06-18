"""
Module: Reasoning String Generator
Owner: Sahitya
Branch: feature/sahitya-behavioral
Purpose: Generate honest, fact-grounded one-line reasoning per candidate
Input: all signal scores + parsed candidate data
Output: reasoning string per candidate

Rules (from submission_spec.docx Stage 4 checks):
  - Must reference specific facts from the profile
  - Must connect to JD requirements
  - Must acknowledge gaps honestly
  - No hallucination — only facts from the profile
  - Must vary across candidates
  - Tone must match rank position
"""

import json
from pathlib import Path


def build_reasoning(
    parsed: dict,
    features: dict,
    behavioral: dict,
    final_score: float,
    rank: int
) -> str:
    """
    Build a specific, honest, fact-grounded reasoning string.
    Every claim must come from the actual profile data.
    """

    cid           = parsed["candidate_id"]
    title         = parsed["current_title"] or "Unknown Title"
    company       = parsed["current_company"] or ""
    years         = parsed["years_exp"]
    country       = parsed["country"]
    notice        = parsed["notice_days"]
    open_work     = parsed["open_to_work"]
    response_rate = parsed["response_rate"]
    location_ok   = parsed["location_eligible"]
    willing_rel   = parsed["willing_relocate"]

    # Feature flags
    systems_score   = features["systems_built_score"]
    prod_ml_score   = features["production_ml_score"]
    consulting_only = features["consulting_only"]
    domain_mismatch = features["domain_mismatch"]
    honeypot        = features["is_honeypot"]
    skill_mismatch  = features["skill_career_mismatch"]
    chatgpt         = features["chatgpt_boilerplate"]
    disqualified    = features["is_disqualified"]
    edu_tier        = features["edu_score"]

    # Behavioral
    recency         = behavioral["recency_score"]
    last_active     = behavioral["last_active_date"]

    # Top skills (up to 3 relevant ones)
    skill_list      = parsed["skill_list"]
    relevant_skills = _pick_relevant_skills(skill_list)

    # ── Build parts ───────────────────────────────────────────────────────

    parts = []

    # Part 1: Who they are
    if company:
        parts.append(f"{title} at {company}, {years:.1f} yrs exp")
    else:
        parts.append(f"{title}, {years:.1f} yrs exp")

    # Part 2: Strongest positive signal
    if systems_score >= 0.5:
        parts.append("career history shows ranking/search/reco systems built")
    elif prod_ml_score >= 0.5:
        parts.append("production ML deployment experience detected")
    elif relevant_skills:
        parts.append(f"relevant skills: {', '.join(relevant_skills[:3])}")

    # Part 3: Behavioral signal
    if open_work and recency >= 0.75:
        parts.append(f"open to work, active recently")
    elif open_work:
        parts.append("open to work")
    elif recency >= 0.75:
        parts.append("recently active on platform")

    parts.append(f"response rate {response_rate:.2f}")

    # Part 4: Honest concerns / gaps
    concerns = []

    if honeypot:
        concerns.append("profile has inconsistencies (possible honeypot)")
    if domain_mismatch:
        concerns.append("career is non-technical, not a fit for this JD")
    if skill_mismatch and not domain_mismatch:
        concerns.append("AI skills listed but not reflected in career history")
    if chatgpt and domain_mismatch:
        concerns.append("generic AI curiosity summary, no real AI experience")
    if consulting_only:
        concerns.append("consulting-only background (no product company)")
    if not location_ok:
        concerns.append(f"based in {country}, not willing to relocate")
    if notice > 90:
        concerns.append(f"long notice period ({notice} days)")
    if years < 4:
        concerns.append(f"under-experienced for this role ({years:.1f} yrs)")
    if years > 12:
        concerns.append("may be overqualified")

    if concerns:
        parts.append("concern: " + "; ".join(concerns[:2]))  # max 2 concerns

    # ── Combine and trim to ~150 chars ────────────────────────────────────
    reasoning = " | ".join(parts)
    if len(reasoning) > 200:
        reasoning = reasoning[:197] + "..."

    return reasoning


def _pick_relevant_skills(skill_list: list) -> list:
    """Pick the most relevant skills for the JD from the skill list."""
    TARGET_SKILLS = {
        "python", "embeddings", "vector", "retrieval", "ranking",
        "recommendation", "nlp", "transformer", "bert", "faiss",
        "elasticsearch", "opensearch", "sentence-transformer",
        "hugging face", "pytorch", "tensorflow", "scikit-learn",
        "xgboost", "lightgbm", "mlflow", "pinecone", "weaviate",
        "qdrant", "milvus", "spark", "kafka", "airflow", "sql",
        "information retrieval", "search", "re-ranking", "ltr",
        "machine learning", "deep learning", "fine-tuning", "rag",
        "llm", "bm25", "weaviate", "haystack", "langchain"
    }

    relevant = []
    for skill in skill_list:
        name = skill["name"].lower()
        prof = skill["proficiency"]
        dur  = skill["duration_months"]

        # Only include if actually used (duration > 0) and intermediate+
        if dur > 0 and prof in ("intermediate", "advanced", "expert"):
            if any(t in name for t in TARGET_SKILLS):
                relevant.append(skill["name"])

    return relevant[:5]


def generate_all_reasonings(
    parsed_list: list,
    features_dict: dict,
    behavioral_dict: dict,
    ranked_results: list
) -> dict:
    """
    Generate reasoning for all ranked candidates.
    ranked_results: list of (candidate_id, final_score, rank)
    Returns dict: candidate_id -> reasoning string
    """
    reasonings = {}

    for candidate_id, final_score, rank in ranked_results:
        parsed     = next((p for p in parsed_list
                           if p["candidate_id"] == candidate_id), None)
        features   = features_dict.get(candidate_id, {})
        behavioral = behavioral_dict.get(candidate_id, {})

        if parsed is None:
            reasonings[candidate_id] = "Profile data unavailable."
            continue

        reasoning = build_reasoning(
            parsed=parsed,
            features=features,
            behavioral=behavioral,
            final_score=final_score,
            rank=rank
        )
        reasonings[candidate_id] = reasoning

    return reasonings


if __name__ == "__main__":
    # Quick test on first 5 parsed candidates
    import json

    with open("data/parsed_candidates.json", "r") as f:
        parsed_list = json.load(f)

    with open("data/structured_features.json", "r") as f:
        features_dict = json.load(f)

    with open("data/behavioral_scores.json", "r") as f:
        behavioral_dict = json.load(f)

    print("Sample reasoning strings:\n")
    for i, p in enumerate(parsed_list[:5]):
        cid      = p["candidate_id"]
        features = features_dict.get(cid, {})
        behav    = behavioral_dict.get(cid, {})
        r        = build_reasoning(p, features, behav,
                                   final_score=0.5, rank=i+1)
        print(f"[{cid}] {r}")
        print()
