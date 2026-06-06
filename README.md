# Redrob Intelligent Candidate Ranking

> **Track 1 — Intelligent Candidate Discovery & Ranking Challenge**
> Redrob AI Hackathon | Submission Deadline: July 2, 2026

---

## What This Is

A multi-signal, semantics-first candidate ranking system that goes beyond keyword matching to think like a senior technical recruiter. Built for the Redrob AI Hackathon Track 1 challenge.

Given a Job Description for a **Senior AI Engineer** role, this system ranks 5000 candidates by true relevance — detecting whether they've actually built ranking/search/recommendation systems, not just listed the keywords.

---

## Team

| Name | GitHub | Role |
|------|--------|------|
| Sravan | [@sravanyadav-19](https://github.com/sravanyadav-19) | Lead — Scoring Engine & Pipeline |
| Ganesh | [@GorantlaGanesh](https://github.com/GorantlaGanesh) | Semantic Embeddings & Similarity |
| Rajesh | [@rayesh8468](https://github.com/rayesh8468) | Feature Extraction & Data Engineering |
| Sahitya | [@saisahitya-19](https://github.com/saisahitya-19) | Behavioral Signals, Reasoning & Slides |

---

## Submission Assets

| Asset | Location |
|-------|----------|
| Ranked Output CSV | `output/ranked_candidates.csv` |
| Slide Deck (PDF) | `slides/presentation.pdf` |
| Pipeline Entry Point | `src/pipeline.py` |

---

## Scoring Formula

```
Final Score =
  0.35 × semantic_job_match
+ 0.25 × systems_built_score
+ 0.15 × production_ml_score
+ 0.10 × product_company_boost
+ 0.10 × redrob_behavior_score
+ 0.05 × recency_boost
```

---

## How to Run

```bash
# 1. Clone the repo
git clone https://github.com/sravanyadav-19/redrob-intelligent-candidate-ranking.git
cd redrob-intelligent-candidate-ranking

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add data (not committed to repo)
# Place candidates.jsonl in data/raw/
# Place job_description content in data/job_description.txt

# 4. Run full pipeline
python src/pipeline.py

# Output will be at output/ranked_candidates.csv
```

> Full pipeline runs in under 5 minutes on CPU with 16GB RAM. No network calls during inference.

---

## Project Structure

```
redrob-intelligent-candidate-ranking/
├── data/
│   ├── raw/                  # candidates.jsonl (NOT committed — gitignored)
│   └── job_description.txt   # JD text
├── src/
│   ├── pipeline.py           # Main entry point
│   ├── parser.py             # Candidate profile parser
│   ├── embedder.py           # Semantic embeddings
│   ├── feature_extractor.py  # Structured rule-based features
│   ├── behavioral_signals.py # Redrob behavioral signal scorer
│   ├── scorer.py             # Final weighted scoring engine
│   └── reasoning.py          # Reasoning string generator
├── output/
│   └── ranked_candidates.csv # Final submission file
├── slides/
│   └── presentation.pdf      # Slide deck
├── notebooks/
│   └── exploration.ipynb     # EDA and analysis
├── tests/
│   └── test_validator.py     # Submission format validator
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| `sentence-transformers` | Semantic embeddings (all-MiniLM-L6-v2) |
| `scikit-learn` | Cosine similarity, TF-IDF fallback |
| `pandas` | Data processing |
| `numpy` | Numerical operations |
| `tqdm` | Progress bars |
| `python-docx` | JD parsing |

---

*Built for Redrob AI Hackathon 2026*
