"""
Module: Main Pipeline
Owner: Sravan
Branch: feature/sravan-scorer
Purpose: Orchestrate all modules end-to-end
Input: data/raw/candidates.jsonl
Output: output/ranked_candidates.csv
Constraint: Must run in under 5 minutes on CPU, no network calls during inference
"""

import json
import time
import csv
from pathlib import Path

import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from parser import parse_candidate
from embedder import JD_TEXT
from feature_extractor import extract_features
from behavioral_signals import compute_behavior_score
from scorer import rank_candidates
from reasoning import build_reasoning


def run_pipeline(
    candidates_path: str = "data/raw/candidates.jsonl",
    output_path:     str = "output/ranked_candidates.csv",
    top_n:           int = 100,
    team_id:         str = "just_started",
):
    t_total = time.time()

    Path("data").mkdir(exist_ok=True)
    Path("output").mkdir(exist_ok=True)

    # ── STEP 1: Parse all candidates ─────────────────────────────────────
    print("\n[1/5] Parsing candidates...")
    t = time.time()
    parsed_list = []
    with open(candidates_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                raw = json.loads(line)
                parsed_list.append(parse_candidate(raw))
            except Exception as e:
                pass
    print(f"      Parsed {len(parsed_list)} candidates in {time.time()-t:.1f}s")

    # ── STEP 2: Semantic embeddings ───────────────────────────────────────
    print("\n[2/5] Computing semantic scores...")
    t = time.time()

    # Check if cached
    sem_cache = Path("data/semantic_scores.json")
    if sem_cache.exists():
        print("      Loading cached semantic scores...")
        with open(sem_cache, "r") as f:
            semantic_scores = json.load(f)
    else:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.preprocessing import normalize
        import numpy as np

        candidate_ids   = [p["candidate_id"] for p in parsed_list]
        candidate_texts = []
        for p in parsed_list:
            parts = []
            if p["current_title"]:
                parts.append(p["current_title"])
                parts.append(p["current_title"])
            if p["experience_text"]:
                parts.append(p["experience_text"])
            if p["summary"]:
                parts.append(p["summary"])
            if p["skills_text"]:
                parts.append(p["skills_text"])
            candidate_texts.append(" ".join(parts))

        vectorizer = TfidfVectorizer(
            max_features=20000, ngram_range=(1, 2),
            sublinear_tf=True, min_df=2, max_df=0.95,
            strip_accents="unicode",
            token_pattern=r"(?u)\b[a-zA-Z][a-zA-Z0-9\-\.]+\b"
        )
        all_texts    = [JD_TEXT] + candidate_texts
        tfidf_matrix = vectorizer.fit_transform(all_texts)
        jd_vec       = normalize(tfidf_matrix[0], norm="l2")
        cand_norm    = normalize(tfidf_matrix[1:], norm="l2")
        similarities = (cand_norm @ jd_vec.T).toarray().flatten()

        semantic_scores = {
            cid: round(float(sim), 6)
            for cid, sim in zip(candidate_ids, similarities)
        }
        with open(sem_cache, "w") as f:
            json.dump(semantic_scores, f)

    print(f"      Semantic scores ready in {time.time()-t:.1f}s")

    # ── STEP 3: Feature extraction ────────────────────────────────────────
    print("\n[3/5] Extracting structured features...")
    t = time.time()
    features_dict = {
        p["candidate_id"]: extract_features(p)
        for p in parsed_list
    }
    print(f"      Features extracted in {time.time()-t:.1f}s")

    # ── STEP 4: Behavioral signals ────────────────────────────────────────
    print("\n[4/5] Scoring behavioral signals...")
    t = time.time()
    behavioral_dict = {
        p["candidate_id"]: compute_behavior_score(p)
        for p in parsed_list
    }
    print(f"      Behavioral scores ready in {time.time()-t:.1f}s")

    # ── STEP 5: Score + rank + reasoning ─────────────────────────────────
    print("\n[5/5] Ranking candidates...")
    t = time.time()
    top_candidates = rank_candidates(
        parsed_list     = parsed_list,
        semantic_scores = semantic_scores,
        features_dict   = features_dict,
        behavioral_dict = behavioral_dict,
        top_n           = top_n,
    )

    # Generate reasoning
    ranked_tuples = [
        (r["candidate_id"], r["final_score"], r["rank"])
        for r in top_candidates
    ]
    parsed_lookup = {p["candidate_id"]: p for p in parsed_list}

    reasonings = {}
    for cid, score, rank in ranked_tuples:
        p    = parsed_lookup.get(cid, {})
        feat = features_dict.get(cid, {})
        beh  = behavioral_dict.get(cid, {})
        reasonings[cid] = build_reasoning(p, feat, beh, score, rank)

    print(f"      Ranking + reasoning done in {time.time()-t:.1f}s")

    # ── Write CSV ─────────────────────────────────────────────────────────
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["candidate_id", "rank", "score", "reasoning"])
        for r in top_candidates:
            cid = r["candidate_id"]
            writer.writerow([
                cid,
                r["rank"],
                round(r["final_score"], 6),
                reasonings.get(cid, ""),
            ])

    elapsed = time.time() - t_total
    print(f"\n✅ Pipeline complete in {elapsed:.1f}s")
    print(f"   Output: {output_path}")
    print(f"\n   Top 5:")
    for r in top_candidates[:5]:
        print(f"   #{r['rank']} {r['candidate_id']} "
              f"score={r['final_score']:.4f} | "
              f"{reasonings.get(r['candidate_id'], '')[:80]}")

    return top_candidates


if __name__ == "__main__":
    run_pipeline()
