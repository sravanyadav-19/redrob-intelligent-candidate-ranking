# Ganesh — Your Complete Guide
# Branch: feature/ganesh-embedder

---

## Your Job in One Line

Build the semantic similarity module — embed the JD and all 5000 candidate profiles, compute how closely each candidate's career matches the job description.

---

## First Time Git Setup (do this once)

```bash
# 1. Accept the GitHub collaborator invite (check your email)

# 2. Clone the repo
git clone https://github.com/sravanyadav-19/redrob-intelligent-candidate-ranking.git
cd redrob-intelligent-candidate-ranking

# 3. Set your identity
git config user.name "Ganesh"
git config user.email "your-email@gmail.com"

# 4. Switch to your branch
git checkout feature/ganesh-embedder

# 5. Confirm you're on the right branch
git branch
# Should show: * feature/ganesh-embedder
```

---

## Daily Workflow

### Start of every work session:
```bash
git checkout dev
git pull origin dev
git checkout feature/ganesh-embedder
git merge dev
```

### End of every work session:
```bash
git add .
git commit -m "feat: describe what you did"
git push origin feature/ganesh-embedder
```

---

## Your Task — Phase by Phase

### Phase 1 (June 6–10): Parser
File to create: `src/parser.py`

Read `data/raw/candidates.jsonl` line by line. For each candidate, extract:
- `candidate_id`
- `name`
- `headline`
- `summary`
- `current_title`
- `current_company`
- `years_of_experience`
- All past job titles and descriptions (join into one string called `experience_text`)
- All skill names (join into one string called `skills_text`)

Handle nulls: if any field is missing, use `""` (empty string), never crash.

Save output as `data/parsed_candidates.json`

### Phase 2 (June 11–20): Embedder
File to create: `src/embedder.py`

- Load model: `sentence-transformers/all-MiniLM-L6-v2`
- Build a text blob per candidate: `current_title + " " + experience_text + " " + skills_text`
- Embed the JD text (Sravan will give you this string)
- Embed all 5000 candidate blobs
- Compute cosine similarity between JD embedding and each candidate
- Save: `data/semantic_scores.json` → format: `{"CAND_001": 0.734, "CAND_002": 0.521, ...}`
- Also save embeddings to disk so pipeline doesn't re-compute every run

### Phase 3 (June 21–24): Tuning
- Test 2-3 different text blob constructions (title only vs title+experience vs full)
- Pick the one that gives the most sensible top-20 when you read them
- Document your choice in a comment in the code

---

## When Your Task is Done — Open a Pull Request

1. Go to: https://github.com/sravanyadav-19/redrob-intelligent-candidate-ranking
2. Click "Compare & pull request" on your branch
3. Base: `dev`, Title: `[Ganesh] Embedder module complete`
4. Assign Sravan as reviewer
5. Do NOT merge yourself — wait for Sravan

---

## Important Rules

- Only edit files in `src/embedder.py` and `src/parser.py`
- Do NOT touch `pipeline.py` or `scorer.py`
- Do NOT commit `candidates.jsonl` — it's gitignored
- If stuck for more than 2 hours — message Sravan with: what you tried, where it fails
