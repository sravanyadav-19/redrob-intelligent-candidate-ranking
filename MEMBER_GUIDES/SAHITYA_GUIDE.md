# Sahitya — Your Complete Guide
# Branch: feature/sahitya-behavioral

---

## Your Job in One Line

Build the behavioral signal scorer (from Redrob platform data), generate the reasoning string for each candidate, validate the submission format, and own the slide deck.

---

## First Time Git Setup (do this once)

```bash
# 1. Accept the GitHub collaborator invite (check your email)

# 2. Clone the repo
git clone https://github.com/sravanyadav-19/redrob-intelligent-candidate-ranking.git
cd redrob-intelligent-candidate-ranking

# 3. Set your identity
git config user.name "Sahitya"
git config user.email "your-email@gmail.com"

# 4. Switch to your branch
git checkout feature/sahitya-behavioral

# 5. Confirm you're on the right branch
git branch
# Should show: * feature/sahitya-behavioral
```

---

## Daily Workflow

### Start of every work session:
```bash
git checkout dev
git pull origin dev
git checkout feature/sahitya-behavioral
git merge dev
```

### End of every work session:
```bash
git add .
git commit -m "feat: describe what you did"
git push origin feature/sahitya-behavioral
```

---

## Your Task — Phase by Phase

### Phase 1 (June 6–10): Submission Format + Validator
File to create: `tests/test_validator.py`

Write a script that checks if a CSV file is a valid submission:
- Exactly 100 rows (not counting header)
- Exactly 4 columns: `candidate_id`, `rank`, `score`, `reasoning`
- Ranks are integers 1 to 100, no duplicates
- Scores are non-increasing (rank 1 has highest score, rank 100 has lowest)
- If two scores are equal, lower candidate_id comes first
- `reasoning` column is never empty

Also create a dummy test CSV with 100 fake rows and confirm your validator accepts it.

Commit: `feat: submission validator complete`

Also this week: open the slide template link Sravan sends you.
List out exactly what content goes on each of the 9 slides (just bullet points).
Save as `slides/slide_outline.md`

---

### Phase 2 (June 11–20): Behavioral Signals + Reasoning

**File 1: `src/behavioral_signals.py`**

For each candidate, read from their `redrob_signals` section and compute:

**`recency_score`** (how recently were they active):
- Last active 0–7 days ago → 1.0
- 8–30 days → 0.80
- 31–90 days → 0.55
- 91–180 days → 0.30
- 181–365 days → 0.10
- Over 365 days → 0.02
- If `last_active_date` is null → 0.20

**`response_rate`**: use the value directly from redrob_signals (already 0–1). If null → 0.30

**`open_to_work_score`**: if `open_to_work` flag is True → 1.0, else → 0.60. If null → 0.50

**`notice_score`** (based on notice_period_days):
- 0–30 days → 1.0
- 31–60 days → 0.80
- 61–90 days → 0.60
- 91+ days → 0.40
- If null → 0.70

**`behavior_score`** (final combined):
```
behavior_score = (0.40 × recency_score) + (0.30 × response_rate) + (0.20 × open_to_work_score) + (0.10 × notice_score)
```

Save output: `data/behavioral_scores.json`
Format: `{"CAND_001": {"behavior_score": 0.72, "recency_score": 0.8, ...}, ...}`

---

**File 2: `src/reasoning.py`**

For each candidate, generate a one-line reasoning string explaining their rank.

Format rule:
`"{current_title}, {X} yrs exp; {best signal}; response rate {Y}"`

Examples:
- `"Senior ML Engineer, 7 yrs; built search ranking at Swiggy; response rate 0.82"`
- `"Data Scientist, 5 yrs; production embeddings at Razorpay; open to work"`
- `"Software Engineer, 3 yrs; no ranking/search systems detected; low activity"`

Rules:
- Always include title, years exp, response rate
- If `systems_built_score > 0.5` → mention the strongest signal from experience
- If `consulting_only_flag = True` → add "consulting-only background"
- If `recency_score < 0.3` → add "low recent activity"
- Keep it under 120 characters

Save output: `data/reasoning_strings.json`
Format: `{"CAND_001": "Senior ML Engineer, 7 yrs; built ranking at Swiggy; response rate 0.82"}`

---

### Phase 3 (June 21–24): Slides
Fill in slides 1–9 using the outline you made in Phase 1.
Sravan will give you the results, metrics, and architecture diagram.
You write the content, make it clean and professional.
Export as PDF → `slides/presentation.pdf`
Commit: `docs: final slide deck added`

---

### Phase 4 (June 25–28): Final Polish
- Proofread entire slide deck
- Fill in `submission_metadata_template.yaml` (Sravan will share this)
- Confirm `output/ranked_candidates.csv` passes the validator one final time
- Commit everything

---

## When Your Task is Done — Open a Pull Request

1. Go to: https://github.com/sravanyadav-19/redrob-intelligent-candidate-ranking
2. Click "Compare & pull request" on your branch
3. Base: `dev`, Title: `[Sahitya] Behavioral signals + reasoning complete`
4. Assign Sravan as reviewer
5. Do NOT merge yourself — wait for Sravan

---

## Important Rules

- Only edit: `src/behavioral_signals.py`, `src/reasoning.py`, `tests/test_validator.py`, `slides/`
- Do NOT touch `pipeline.py`, `scorer.py`, `embedder.py`, `feature_extractor.py`
- Do NOT commit `candidates.jsonl`
- If stuck for more than 2 hours — message Sravan with: what you tried, where it fails
