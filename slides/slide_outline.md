# Slide Deck Outline — 9 Slides
# To be filled by Sahitya | Template: Redrob Hackathon PPT

---

## Slide 1 — Cover
- Team name
- Problem statement: "Intelligent Candidate Discovery & Ranking"
- Track: Track 1
- Team leader: Sravan
- All 4 member names

## Slide 2 — Solution Overview
- What we built: multi-signal ranking system
- What makes it different: not keyword matching — career trajectory inference
- Key insight: "A candidate who built a feed ranking system at Swiggy ranks higher than one who listed RAG as a skill"

## Slide 3 — JD Understanding & Candidate Evaluation
- How we parsed the JD (seniority, domain, must-have signals)
- What signals we extracted from candidates (systems built, production ML, company type)
- Behavioral signals from Redrob platform

## Slide 4 — Ranking Methodology
- The 6-signal scoring formula with weights
- Why each weight was chosen
- Hard disqualifier logic (consulting-only, domain mismatch, title-chasing)
- Tiebreak rule

## Slide 5 — Explainability & Data Validation
- How we generate the reasoning string per candidate
- How we handle null/missing fields (never crash, use safe defaults)
- How we detect fake AI keyword stuffing (domain mismatch flag)

## Slide 6 — End-to-End Workflow
- Step-by-step: JD → parse → embed → extract features → score → rank → output
- Input: candidates.jsonl + JD text
- Output: ranked_candidates.csv

## Slide 7 — System Architecture
- Diagram of modules: parser → embedder → feature_extractor → behavioral_signals → scorer → pipeline
- Show data flow between modules
- Show output format

## Slide 8 — Results & Performance
- Top 5 ranked candidates with reasoning strings
- Runtime: X seconds on CPU
- Score distribution (strong candidates vs noise)

## Slide 9 — Technologies Used + Submission Assets
- Tech: sentence-transformers, pandas, scikit-learn, numpy, tqdm
- GitHub repo link
- Ranked output CSV confirmed
- Team members
