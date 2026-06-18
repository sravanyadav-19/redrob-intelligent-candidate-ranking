"""
Module: Semantic Embedder
Owner: Ganesh
Branch: feature/ganesh-embedder
Purpose: Compute semantic similarity between JD and all candidate profiles.
         Uses TF-IDF + cosine similarity for CPU speed on 100K candidates.
         Pre-computes and caches results so pipeline runs in < 5 minutes.
Input: data/parsed_candidates.json + data/job_description.txt
Output: data/semantic_scores.json
"""

import json
import time
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize
import numpy as np


# ── JD text ───────────────────────────────────────────────────────────────────
# Full JD focused on what matters for ranking:
# ranking/search/reco systems, production ML, embeddings, vector DBs

JD_TEXT = """
Senior AI Engineer founding team Redrob AI Series A talent intelligence platform.
Own the intelligence layer ranking retrieval matching systems.
Production experience embeddings-based retrieval systems sentence-transformers
OpenAI embeddings BGE E5 deployed real users embedding drift index refresh
retrieval quality regression production.
Vector databases hybrid search infrastructure Pinecone Weaviate Qdrant Milvus
OpenSearch Elasticsearch FAISS operational experience.
Strong Python production code quality.
Evaluation frameworks ranking systems NDCG MRR MAP offline-to-online correlation
A/B test interpretation.
Built ranking search recommendation systems product companies not services.
Shipped end-to-end ranking search recommendation system real users meaningful scale.
Strong opinions retrieval hybrid dense evaluation offline online LLM integration
fine-tune prompt systems actually built.
5 to 9 years experience applied ML AI roles product companies not pure services.
Learning to rank XGBoost neural LLM fine-tuning LoRA QLoRA PEFT.
Disqualifiers: pure research no production deployment consulting only TCS Infosys
Wipro Accenture Cognizant Capgemini career only services no product company.
Computer vision speech robotics without NLP IR exposure disqualified.
Active on platform recently open to work willing to relocate Pune Noida India.
Startup product company AI SaaS exposure preferred.
Scrappy product engineering attitude ship working ranker learn from real users.
Embeddings retrieval ranking recommendation search systems production deployed.
"""


def build_candidate_text(parsed: dict) -> str:
    """
    Build text blob for embedding.
    Weights experience descriptions highest — that's where real signal is.
    """
    parts = []

    # Current title (repeat for weight)
    title = parsed.get("current_title", "")
    if title:
        parts.append(title)
        parts.append(title)  # repeat = more weight

    # Experience text (most important)
    exp = parsed.get("experience_text", "")
    if exp:
        parts.append(exp)

    # Summary
    summary = parsed.get("summary", "")
    if summary:
        parts.append(summary)

    # Skills (lighter weight)
    skills = parsed.get("skills_text", "")
    if skills:
        parts.append(skills)

    return " ".join(parts)


def compute_semantic_scores(
    parsed_path: str,
    output_path: str,
    jd_text: str = JD_TEXT
) -> dict:

    parsed_path = Path(parsed_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # ── Load parsed candidates ────────────────────────────────────────────
    print(f"Loading: {parsed_path}")
    t0 = time.time()
    with open(parsed_path, "r", encoding="utf-8") as f:
        parsed_list = json.load(f)
    print(f"Loaded {len(parsed_list)} candidates in {time.time()-t0:.1f}s")

    # ── Build text blobs ──────────────────────────────────────────────────
    print("Building text blobs...")
    t1 = time.time()
    candidate_ids   = [p["candidate_id"] for p in parsed_list]
    candidate_texts = [build_candidate_text(p) for p in parsed_list]
    print(f"Text blobs built in {time.time()-t1:.1f}s")

    # ── TF-IDF vectorization ──────────────────────────────────────────────
    print("Fitting TF-IDF vectorizer...")
    t2 = time.time()

    vectorizer = TfidfVectorizer(
        max_features=20000,
        ngram_range=(1, 2),       # unigrams + bigrams
        sublinear_tf=True,        # log normalization
        min_df=2,                 # ignore very rare terms
        max_df=0.95,              # ignore very common terms
        strip_accents="unicode",
        analyzer="word",
        token_pattern=r"(?u)\b[a-zA-Z][a-zA-Z0-9\-\.]+\b"
    )

    # Fit on JD + all candidate texts combined
    all_texts = [jd_text] + candidate_texts
    tfidf_matrix = vectorizer.fit_transform(all_texts)
    print(f"TF-IDF fitted in {time.time()-t2:.1f}s | "
          f"vocab size: {len(vectorizer.vocabulary_)}")

    # ── Cosine similarity ─────────────────────────────────────────────────
    print("Computing cosine similarities...")
    t3 = time.time()

    jd_vector         = tfidf_matrix[0]           # first row = JD
    candidate_matrix  = tfidf_matrix[1:]           # rest = candidates

    # Normalize for cosine similarity
    jd_vec_norm  = normalize(jd_vector, norm="l2")
    cand_norm    = normalize(candidate_matrix, norm="l2")

    # Use sparse dot product — avoids memory explosion
    similarities = (cand_norm @ jd_vec_norm.T).toarray().flatten()
    print(f"Similarities computed in {time.time()-t3:.1f}s")

    # ── Save ──────────────────────────────────────────────────────────────
    scores_dict = {
        cid: round(float(sim), 6)
        for cid, sim in zip(candidate_ids, similarities)
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(scores_dict, f)

    total_time = time.time() - t0
    print(f"\nSemantic scoring complete in {total_time:.1f}s")
    print(f"  Min score:  {min(similarities):.4f}")
    print(f"  Max score:  {max(similarities):.4f}")
    print(f"  Mean score: {similarities.mean():.4f}")
    print(f"Saved: {output_path}")

    return scores_dict


if __name__ == "__main__":
    compute_semantic_scores(
        parsed_path="data/parsed_candidates.json",
        output_path="data/semantic_scores.json"
    )
