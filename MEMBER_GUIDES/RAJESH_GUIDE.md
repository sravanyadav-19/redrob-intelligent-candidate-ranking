# Rajesh — Your Complete Guide
# Branch: feature/rajesh-feature-extractor

---

## Your Job in One Line

Set up the project environment and build the structured feature extractor — a Python script that detects, using rules and keywords, whether a candidate has actually built ranking/search/recommendation systems.

---

## First Time Git Setup (do this once)

```bash
# 1. Accept the GitHub collaborator invite (check your email)

# 2. Clone the repo
git clone https://github.com/sravanyadav-19/redrob-intelligent-candidate-ranking.git
cd redrob-intelligent-candidate-ranking

# 3. Set your identity
git config user.name "Rajesh"
git config user.email "your-email@gmail.com"

# 4. Switch to your branch
git checkout feature/rajesh-feature-extractor

# 5. Confirm you're on the right branch
git branch
# Should show: * feature/rajesh-feature-extractor
```

---

## Daily Workflow

### Start of every work session:
```bash
git checkout dev
git pull origin dev
git checkout feature/rajesh-feature-extractor
git merge dev
```

### End of every work session:
```bash
git add .
git commit -m "feat: describe what you did"
git push origin feature/rajesh-feature-extractor
```

---

## Your Task — Phase by Phase

### Phase 1 (June 6–10): Environment + Data Audit
1. Install all dependencies:
```bash
pip install sentence-transformers numpy pandas scikit-learn tqdm python-docx torch
pip freeze > requirements.txt
```

2. Create this exact folder structure:
```
data/
  raw/           ← put candidates.jsonl here (never commit this)
  job_description.txt
src/
output/
slides/
notebooks/
tests/
```

3. Write a data audit script `src/audit.py` that:
   - Reads `candidates.jsonl` line by line
   - Counts: total candidates, how many have null summary, null skills, null redrob_signals, null experience
   - Prints and saves results to `data/audit_report.txt`

Commit: `feat: environment setup and data audit complete`

---

### Phase 2 (June 11–20): Feature Extractor
File to create: `src/feature_extractor.py`

For each parsed candidate (use `data/parsed_candidates.json` from Ganesh), detect these features:

**Feature 1: `systems_built_score` (0.0 to 1.0)**
Search through `experience_text` for these keywords:
- "ranking", "search", "recommendation", "recommender", "retrieval", "relevance", "ranking system", "search engine", "feed ranking"
- Each unique keyword found = +0.15, cap at 1.0

**Feature 2: `production_ml_score` (0.0 to 1.0)**
Search through `experience_text` for:
- "production", "deployed", "shipped", "A/B test", "inference", "vector", "embedding", "NDCG", "MRR", "latency", "real users"
- Each unique keyword found = +0.12, cap at 1.0

**Feature 3: `consulting_only_flag` (True/False)**
If ALL past companies are in this list → True:
- TCS, Tata Consultancy, Infosys, Wipro, Accenture, Cognizant, Capgemini, HCL, Tech Mahindra, Mphasis, Hexaware

**Feature 4: `product_company_boost` (0.0 or 1.0)**
If at least ONE past company is NOT in the consulting list → 1.0, else 0.0

**Feature 5: `title_chasing_flag` (True/False)**
If: (total number of companies > 3) AND (total_experience / number_of_companies < 1.5 years) → True

**Feature 6: `domain_mismatch_flag` (True/False)**
If current title contains any of: "marketing", "sales", "admin", "HR", "finance", "operations"
AND experience_text does NOT contain "ML", "AI", "machine learning", "data" → True

Save output: `data/structured_features.json`
Format: `{"CAND_001": {"systems_built_score": 0.6, "production_ml_score": 0.4, ...}, ...}`

---

### Phase 3 (June 21–24): Pipeline Runner
- Run the full pipeline end-to-end: `python src/pipeline.py`
- Time it — must finish in under 5 minutes
- Catch any crashes on null/missing data, report to Sravan
- Generate `output/ranked_candidates.csv`
- Run it through the validator: `python tests/test_validator.py`
- Confirm it passes — report back

---

## When Your Task is Done — Open a Pull Request

1. Go to: https://github.com/sravanyadav-19/redrob-intelligent-candidate-ranking
2. Click "Compare & pull request" on your branch
3. Base: `dev`, Title: `[Rajesh] Feature extractor complete`
4. Assign Sravan as reviewer
5. Do NOT merge yourself — wait for Sravan

---

## Important Rules

- Only edit: `src/feature_extractor.py`, `src/audit.py`
- Do NOT touch `pipeline.py`, `scorer.py`, `embedder.py`
- Do NOT commit `candidates.jsonl` — it's gitignored, keep it in `data/raw/` locally
- If stuck for more than 2 hours — message Sravan with: what you tried, where it fails
