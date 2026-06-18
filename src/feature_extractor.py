"""
Module: Structured Feature Extractor
Owner: Rajesh
Branch: feature/rajesh-feature-extractor
Purpose: Rule-based detection of systems built, production ML,
         consulting flag, domain mismatch, honeypot signals
Input: data/parsed_candidates.json
Output: data/structured_features.json
"""

import json
import re
from pathlib import Path


# ── Keyword lists ─────────────────────────────────────────────────────────────

RANKING_SEARCH_RECO_KEYWORDS = [
    "ranking", "search", "recommendation", "recommender", "retrieval",
    "relevance", "ranking system", "search engine", "feed ranking",
    "learning to rank", "learning-to-rank", "ltr", "reranking", "re-ranking",
    "candidate retrieval", "item ranking", "personalization", "personalized",
    "recall", "precision", "ndcg", "mrr", "map@", "retrieval system",
    "vector search", "semantic search", "hybrid search", "dense retrieval",
    "bm25", "elasticsearch", "opensearch", "solr", "query understanding",
    "query rewriting", "ranking model", "ranker", "pointwise", "pairwise",
    "listwise", "xgboost rank", "lightgbm rank"
]

PRODUCTION_ML_KEYWORDS = [
    "production", "deployed", "shipped", "a/b test", "a/b testing",
    "inference", "serving", "real users", "embedding", "embeddings",
    "vector db", "vector database", "pinecone", "weaviate", "qdrant",
    "milvus", "faiss", "annoy", "scann", "feature store", "mlflow",
    "kubeflow", "mlops", "model monitoring", "drift", "latency",
    "throughput", "scalab", "bert", "transformer", "sentence-transformer",
    "fine-tun", "fine tuning", "rag", "retrieval augmented",
    "llm", "large language model", "openai", "hugging face",
    "offline eval", "online eval", "offline-to-online", "feedback loop",
    "click-through", "dwell time", "engagement metric", "revenue per"
]

NON_TECHNICAL_TITLES = [
    "marketing manager", "operations manager", "hr manager", "accountant",
    "sales executive", "content writer", "graphic designer", "civil engineer",
    "mechanical engineer", "business analyst", "customer support",
    "project manager", "product manager", "brand manager", "seo",
    "social media", "finance", "accounting", "procurement"
]

CHATGPT_BOILERPLATE = [
    "i've experimented with chatgpt",
    "experimented with chatgpt",
    "how ai tools could augment my work",
    "apply my domain expertise alongside emerging ai",
    "open to roles where i can apply my domain expertise"
]

CORE_AI_SKILLS = [
    "python", "embeddings", "vector", "retrieval", "ranking",
    "recommendation", "nlp", "transformer", "bert", "faiss",
    "elasticsearch", "opensearch", "sentence-transformer",
    "hugging face", "pytorch", "tensorflow", "scikit-learn",
    "xgboost", "lightgbm", "mlflow", "kubeflow", "airflow",
    "spark", "kafka", "pinecone", "weaviate", "qdrant", "milvus"
]


# ── Scoring helpers ───────────────────────────────────────────────────────────

def keyword_score(text: str, keywords: list, per_hit: float, cap: float) -> float:
    text_lower = text.lower()
    hits = sum(1 for kw in keywords if kw in text_lower)
    return min(hits * per_hit, cap)


def detect_chatgpt_boilerplate(summary: str) -> bool:
    s = summary.lower()
    return any(phrase in s for phrase in CHATGPT_BOILERPLATE)


def detect_domain_mismatch(current_title: str, experience_text: str,
                            summary: str, skills_text: str) -> bool:
    """
    True if person is clearly non-technical (marketing/HR/sales/etc.)
    AND their experience text has no real ML/AI/engineering signal.
    """
    title_lower = current_title.lower()
    is_nontechnical_title = any(t in title_lower for t in NON_TECHNICAL_TITLES)

    combined = (experience_text + " " + summary).lower()
    has_technical_exp = any(kw in combined for kw in [
        "machine learning", "deep learning", "neural", "python",
        "data engineer", "ml engineer", "ai engineer", "nlp",
        "ranking", "recommendation", "retrieval", "embedding",
        "model", "algorithm", "pipeline", "spark", "sql", "analytics"
    ])

    return is_nontechnical_title and not has_technical_exp


def detect_skill_career_mismatch(skill_list: list, experience_text: str,
                                  summary: str) -> bool:
    """
    Detects keyword stuffing: AI skills listed but zero AI in career.
    Example: CAND_0000021 — Project Manager with Pinecone/FAISS listed as skills
    but entire career is brand/marketing/customer support.
    """
    skill_names = [s["name"].lower() for s in skill_list]
    ai_skills_count = sum(1 for s in skill_names
                          if any(core in s for core in CORE_AI_SKILLS))

    combined_exp = (experience_text + " " + summary).lower()
    has_ai_in_exp = any(kw in combined_exp for kw in [
        "machine learning", "ml model", "ai model", "neural network",
        "deep learning", "nlp", "recommendation", "ranking", "retrieval",
        "embedding", "vector", "transformer", "bert", "python script",
        "data science", "data scientist", "ml engineer", "ai engineer"
    ])

    # 4+ AI skills listed but zero AI experience in career = stuffing
    return ai_skills_count >= 4 and not has_ai_in_exp


def experience_depth_score(years_exp: float) -> float:
    """
    Score experience against JD sweet spot of 5-9 years.
    4-10 years = good range.
    """
    if years_exp < 2:
        return 0.1
    elif years_exp < 4:
        return 0.4
    elif years_exp <= 9:
        # Peak at 6-7 years
        return min(1.0, 0.6 + (years_exp - 4) * 0.1)
    elif years_exp <= 12:
        return 0.85
    else:
        return 0.70  # overqualified slight reduction


def education_score(edu_tier: str) -> float:
    tier_scores = {
        "tier_1": 1.0,
        "tier_2": 0.80,
        "tier_3": 0.60,
        "tier_4": 0.40,
        "unknown": 0.35
    }
    return tier_scores.get(edu_tier, 0.35)


# ── Main extraction function ──────────────────────────────────────────────────

def extract_features(parsed: dict) -> dict:
    """
    Extract all structured features from a parsed candidate dict.
    Returns a flat dict of feature scores and flags.
    """
    cid              = parsed["candidate_id"]
    experience_text  = parsed["experience_text"]
    skills_text      = parsed["skills_text"]
    skill_list       = parsed["skill_list"]
    summary          = parsed["summary"]
    current_title    = parsed["current_title"]
    years_exp        = parsed["years_exp"]
    edu_tier         = parsed["edu_tier"]
    consulting_only  = parsed["consulting_only"]
    has_product_co   = parsed["has_product_company"]
    title_chasing    = parsed["title_chasing"]
    is_honeypot      = parsed["is_honeypot"]

    # Combined text for keyword search
    full_text = f"{experience_text} {summary} {skills_text}".lower()
    exp_summary = f"{experience_text} {summary}".lower()

    # ── Feature 1: Systems built score (ranking/search/reco) ─────────────
    systems_built_score = keyword_score(
        exp_summary,  # only from actual experience, not skill keywords
        RANKING_SEARCH_RECO_KEYWORDS,
        per_hit=0.12,
        cap=1.0
    )

    # ── Feature 2: Production ML score ───────────────────────────────────
    production_ml_score = keyword_score(
        exp_summary,
        PRODUCTION_ML_KEYWORDS,
        per_hit=0.10,
        cap=1.0
    )

    # ── Feature 3: Product company boost ─────────────────────────────────
    product_company_boost = 1.0 if has_product_co else 0.0
    if consulting_only:
        product_company_boost = 0.0

    # ── Feature 4: Experience depth ───────────────────────────────────────
    exp_depth_score = experience_depth_score(years_exp)

    # ── Feature 5: Education score ────────────────────────────────────────
    edu_score = education_score(edu_tier)

    # ── Flags ─────────────────────────────────────────────────────────────
    chatgpt_boilerplate    = detect_chatgpt_boilerplate(summary)
    domain_mismatch        = detect_domain_mismatch(
                                current_title, experience_text, summary, skills_text)
    skill_career_mismatch  = detect_skill_career_mismatch(
                                skill_list, experience_text, summary)

    # Combined disqualifier flag
    is_disqualified = (
        is_honeypot or
        domain_mismatch or
        (consulting_only and skill_career_mismatch)
    )

    return {
        "candidate_id":           cid,
        "systems_built_score":    round(systems_built_score, 4),
        "production_ml_score":    round(production_ml_score, 4),
        "product_company_boost":  product_company_boost,
        "exp_depth_score":        round(exp_depth_score, 4),
        "edu_score":              round(edu_score, 4),
        "consulting_only":        consulting_only,
        "title_chasing":          title_chasing,
        "chatgpt_boilerplate":    chatgpt_boilerplate,
        "domain_mismatch":        domain_mismatch,
        "skill_career_mismatch":  skill_career_mismatch,
        "is_honeypot":            is_honeypot,
        "is_disqualified":        is_disqualified,
    }


def extract_all(parsed_path: str, output_path: str):
    parsed_path  = Path(parsed_path)
    output_path  = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Loading parsed candidates from: {parsed_path}")
    with open(parsed_path, "r", encoding="utf-8") as f:
        parsed_list = json.load(f)

    print(f"Extracting features for {len(parsed_list)} candidates...")
    features = [extract_features(p) for p in parsed_list]

    # Stats
    disqualified    = sum(1 for f in features if f["is_disqualified"])
    honeypots       = sum(1 for f in features if f["is_honeypot"])
    domain_mismatch = sum(1 for f in features if f["domain_mismatch"])
    consulting      = sum(1 for f in features if f["consulting_only"])
    chatgpt         = sum(1 for f in features if f["chatgpt_boilerplate"])

    print(f"\nFeature extraction complete:")
    print(f"  Total candidates:     {len(features)}")
    print(f"  Disqualified:         {disqualified}")
    print(f"  Honeypots detected:   {honeypots}")
    print(f"  Domain mismatch:      {domain_mismatch}")
    print(f"  Consulting only:      {consulting}")
    print(f"  ChatGPT boilerplate:  {chatgpt}")

    # Save as dict keyed by candidate_id for fast lookup
    features_dict = {f["candidate_id"]: f for f in features}
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(features_dict, f)

    print(f"\nSaved: {output_path}")
    return features_dict


if __name__ == "__main__":
    extract_all(
        parsed_path="data/parsed_candidates.json",
        output_path="data/structured_features.json"
    )
