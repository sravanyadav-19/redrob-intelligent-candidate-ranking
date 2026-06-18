# Redrob Intelligent Candidate Ranking
### Team: just_started | Track 1 — Intelligent Candidate Discovery

---

## Problem Understanding

Given a Job Description for a **Senior AI Engineer** role at Redrob AI, rank 100,000 candidate profiles by true relevance. The challenge explicitly warns against keyword matching — a candidate who built a feed ranking system at Swiggy without using the word "RAG" is a stronger fit than someone who lists every AI keyword but has a marketing career.

Our system thinks like a senior technical recruiter:
- It reads what candidates actually **built**, not what they listed
- It detects keyword stuffers, consulting-only backgrounds, and honeypot profiles
- It weighs behavioral signals — an inactive candidate is not actually available

---

## Approach

### Why not pure embeddings?

Sentence-transformer embeddings on 100K candidates take 20+ minutes on CPU — beyond the 5-minute constraint. TF-IDF with bigrams, combined with rule-based career signal extraction, runs in **35 seconds** and outperforms pure embedding approaches because the most important signals (did they build a ranking system?) are detectable with keyword rules on experience descriptions.

### Signal hierarchy

```
Final Score =
  0.35 × semantic_job_match       (TF-IDF cosine similarity, JD vs career text)
+ 0.25 × systems_built_score      (ranking/search/reco keywords in experience)
+ 0.15 × production_ml_score      (production deployment signals in experience)
+ 0.10 × product_company_boost    (product vs consulting company history)
+ 0.10 × behavior_score           (recency, response rate, open-to-work, notice)
+ 0.05 × exp_depth_score          (years of experience vs JD sweet spot 5-9 yrs)
```

### Hard disqualifiers
| Condition | Action |
|-----------|--------|
| Honeypot profile (impossible experience) | Cap score at 0.05 |
| Domain mismatch (marketing/HR/sales career) | Cap score at 0.10 |
| Outside India + not willing to relocate | Cap score at 0.10 |
| Consulting-only + AI keyword stuffing | Cap score at 0.15 |
| Consulting-only background | 30% score reduction |

### Behavioral scoring
```
behavior_score =
  0.40 × recency_score        (last active date decay)
+ 0.25 × response_rate        (recruiter response rate from Redrob signals)
+ 0.15 × open_to_work_score   (open to work flag)
+ 0.10 × notice_score         (notice period — sub-30 days preferred)
+ 0.05 × github_score         (GitHub activity, 0 if not linked)
+ 0.05 × profile_completeness
```

### Key edge cases handled
- **Keyword stuffing**: AI skills listed but non-technical career history → flagged
- **ChatGPT boilerplate**: Detected via summary pattern matching → domain mismatch
- **Honeypots**: Expert skill with 0 months usage, or experience gap > 3 years → capped
- **Inverted salary ranges**: min > max → silently swapped
- **Consulting firms**: TCS, Infosys, Wipro, Accenture, Cognizant, HCL, Tech Mahindra, Capgemini, Mphasis, Hexaware, Mindtree

---

## System Architecture

```
candidates.jsonl
      │
      ▼
┌─────────────┐
│  parser.py  │  → Extracts 30+ fields per candidate, detects honeypots,
└─────────────┘    handles nulls, fixes inverted salary ranges
      │
      ├──────────────────────────────────────┐
      ▼                                      ▼
┌──────────────┐                   ┌──────────────────────┐
│ embedder.py  │                   │ feature_extractor.py │
│ TF-IDF +     │                   │ Rule-based keyword   │
│ cosine sim   │                   │ detection on career  │
└──────────────┘                   │ history text         │
      │                            └──────────────────────┘
      │                                      │
      │                   ┌──────────────────┘
      │                   ▼
      │         ┌──────────────────────┐
      │         │ behavioral_signals.py│
      │         │ Redrob platform      │
      │         │ behavioral scoring   │
      │         └──────────────────────┘
      │                   │
      └──────────┬─────────┘
                 ▼
          ┌────────────┐
          │ scorer.py  │  → Weighted combination + disqualifiers + tiebreak
          └────────────┘
                 │
                 ▼
          ┌─────────────┐
          │ reasoning.py│  → Fact-grounded reasoning string per candidate
          └─────────────┘
                 │
                 ▼
          ┌─────────────┐
          │ pipeline.py │  → Orchestrates all modules
          └─────────────┘
                 │
                 ▼
      output/just_started.csv
```

---

## How to Run

### 1. Install dependencies
```bash
pip install scikit-learn numpy
```

### 2. Place data
```
data/raw/candidates.jsonl   ← the 100K candidate pool
```

### 3. Run full pipeline
```bash
python rank.py --candidates data/raw/candidates.jsonl --out output/just_started.csv
```

### 4. Validate output
```bash
python validate_submission.py output/just_started.csv
```

Expected output:
```
Submission is valid.
```

### Runtime
- Full pipeline: **~35 seconds** on CPU
- No GPU required
- No network calls during inference
- Memory: < 4GB RAM

---

## Results

| Metric | Value |
|--------|-------|
| Pipeline runtime | 35 seconds |
| Candidates processed | 100,000 |
| Honeypots detected | 46 |
| Domain mismatches flagged | 47,489 |
| Consulting-only flagged | 9,745 |
| ChatGPT boilerplate detected | 63,304 |
| Top candidate | Lead AI Engineer at Razorpay (score: 0.9652) |

### Top 5 ranked candidates
| Rank | Title | Company | Score |
|------|-------|---------|-------|
| 1 | Lead AI Engineer | Razorpay | 0.9652 |
| 2 | Senior NLP Engineer | Salesforce | 0.9222 |
| 3 | Senior ML Engineer | Zomato | 0.9220 |
| 4 | Senior NLP Engineer | Mad Street Den | 0.9189 |
| 5 | Senior NLP Engineer | Niramai | 0.9179 |

---

## What We Would Improve With More Time

1. **Sentence-transformers** — Pre-compute BGE or MiniLM embeddings offline; use cached vectors at ranking time for better semantic understanding
2. **Learning-to-rank** — With labeled ground truth, train LightGBM ranker on the 6 signals instead of fixed weights
3. **Company reputation signal** — Tier product companies (Razorpay > generic startup) for better product_company_boost
4. **Skill assessment integration** — Use Redrob skill assessment scores as a trust multiplier on listed skills
5. **Recruiter feedback loop** — Log shortlisted candidates, recalibrate weights over time

---

## Team

| Name | Role | GitHub |
|------|------|--------|
| Sravan | Lead — Scoring Engine & Pipeline | [@sravanyadav-19](https://github.com/sravanyadav-19) |
| Ganesh | Semantic Embeddings | [@GorantlaGanesh](https://github.com/GorantlaGanesh) |
| Rajesh | Feature Extraction | [@rayesh8468](https://github.com/rayesh8468) |
| Sahitya | Behavioral Signals & Reasoning | [@saisahitya-19](https://github.com/saisahitya-19) |

---

## Project Structure

```
redrob-intelligent-candidate-ranking/
├── rank.py                    ← Single entry point
├── validate_submission.py     ← Format validator
├── requirements.txt
├── README.md
├── submission_metadata.yaml
├── data/
│   └── raw/
│       └── candidates.jsonl   ← Not committed (gitignored)
├── src/
│   ├── parser.py              ← Candidate profile parser
│   ├── embedder.py            ← TF-IDF semantic scorer
│   ├── feature_extractor.py   ← Rule-based feature extraction
│   ├── behavioral_signals.py  ← Redrob behavioral scoring
│   ├── reasoning.py           ← Reasoning string generator
│   ├── scorer.py              ← Final weighted scoring engine
│   └── pipeline.py            ← Pipeline orchestrator
├── output/
│   └── just_started.csv       ← Final submission file
└── tests/
    └── test_validator.py
```
