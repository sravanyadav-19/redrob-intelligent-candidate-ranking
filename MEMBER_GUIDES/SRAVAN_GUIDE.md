# Sravan — Your Checklist
# Branch: feature/sravan-scorer

---

## Your Role

You are the integration point. Everyone's output flows into your modules.
Your job is not to do everything — it's to make sure everything connects correctly.

---

## Phase 1 (June 6–10)

- [ ] Create GitHub repo (follow SETUP_GITHUB.md exactly)
- [ ] Push initial project structure to `main`
- [ ] Create `dev` branch
- [ ] Add all 3 collaborators
- [ ] Create all 4 feature branches
- [ ] Send each member their guide + branch name
- [ ] Read `candidates.jsonl` yourself — understand the real schema
- [ ] Write the JD text string for Ganesh to embed (clean version, no formatting)
- [ ] Manually review 10 good profiles + 10 bad profiles from the dataset
- [ ] Finalize the exact scoring formula (confirm weights make sense on real data)

---

## Phase 2 (June 11–20)

- [ ] Build `src/scorer.py` — takes all signal scores, outputs final weighted score
- [ ] Build `src/pipeline.py` — orchestrates all modules end to end
- [ ] Implement hard disqualifier logic in scorer:
  - `consulting_only_flag = True` → cap final score at 0.25
  - `domain_mismatch_flag = True` → cap final score at 0.15
  - `title_chasing_flag = True` → reduce final score by 0.10
- [ ] Review Ganesh's PR when ready
- [ ] Review Rajesh's PR when ready

---

## Phase 3 (June 21–24)

- [ ] Integrate all 4 modules into pipeline.py
- [ ] Run full pipeline on 5000 candidates
- [ ] Manually verify top 20 — do they make sense against the JD?
- [ ] Manually verify bottom 20 — are they correctly penalized?
- [ ] Fix any anomalies
- [ ] Confirm runtime < 5 minutes
- [ ] Generate final `output/ranked_candidates.csv`
- [ ] Run through validator — confirm passes

---

## Phase 4 (June 25–28)

- [ ] Final code review — clean comments, remove debug prints
- [ ] Review Sahitya's slides — check technical accuracy
- [ ] Final README review
- [ ] Merge `dev` → `main` (final PR)
- [ ] Confirm repo is public
- [ ] Submit: GitHub URL + PDF slides + ranked CSV

---

## Scoring Formula (your implementation target)

```python
def compute_final_score(signals: dict) -> float:
    score = (
        0.35 * signals["semantic_job_match"]    +
        0.25 * signals["systems_built_score"]   +
        0.15 * signals["production_ml_score"]   +
        0.10 * signals["product_company_boost"] +
        0.10 * signals["behavior_score"]        +
        0.05 * signals["recency_boost"]
    )

    # Hard disqualifiers
    if signals.get("consulting_only_flag"):
        score = min(score, 0.25)
    if signals.get("domain_mismatch_flag"):
        score = min(score, 0.15)
    if signals.get("title_chasing_flag"):
        score = max(0.0, score - 0.10)

    return round(score, 4)
```

## Tiebreak Rule (implement in pipeline)

```python
# Sort by: final_score DESC, systems_built_score DESC, behavior_score DESC, candidate_id ASC
results.sort(key=lambda x: (
    -x["final_score"],
    -x["systems_built_score"],
    -x["behavior_score"],
     x["candidate_id"]
))
```
