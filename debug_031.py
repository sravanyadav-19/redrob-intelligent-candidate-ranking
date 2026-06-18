import json, sys
sys.path.insert(0, 'src')
from scorer import compute_score, apply_disqualifiers, normalize_semantic

with open('data/semantic_scores.json') as f:
    sem = json.load(f)
with open('data/structured_features.json') as f:
    feat = json.load(f)
with open('data/behavioral_scores.json') as f:
    beh = json.load(f)
with open('data/parsed_candidates.json') as f:
    parsed = json.load(f)

cid = 'CAND_0000031'
p   = next(x for x in parsed if x['candidate_id'] == cid)
f   = feat[cid]
b   = beh[cid]

print("=== ALL INPUTS ===")
print("semantic_raw:      ", sem[cid])
print("semantic_norm:     ", normalize_semantic(sem[cid]))
print("systems_built:     ", f['systems_built_score'])
print("production_ml:     ", f['production_ml_score'])
print("product_company:   ", f['product_company_boost'])
print("behavior:          ", b['behavior_score'])
print("exp_depth:         ", f['exp_depth_score'])
print()
print("=== FLAGS ===")
print("is_honeypot:       ", f['is_honeypot'])
print("domain_mismatch:   ", f['domain_mismatch'])
print("consulting_only:   ", f['consulting_only'])
print("skill_mismatch:    ", f['skill_career_mismatch'])
print("location_eligible: ", p['location_eligible'])
print("title_chasing:     ", p['title_chasing'])
print()

base = compute_score(
    sem[cid],
    f['systems_built_score'],
    f['production_ml_score'],
    f['product_company_boost'],
    b['behavior_score'],
    f['exp_depth_score']
)
print("=== SCORES ===")
print("base_score:        ", base)

final = apply_disqualifiers(
    base,
    f['is_honeypot'],
    f['domain_mismatch'],
    f['consulting_only'],
    f['skill_career_mismatch'],
    p['location_eligible'],
    p['title_chasing']
)
print("final_score:       ", final)
print()
print("Rank 100 cutoff:    0.71292")
print("Should be in top100:", final > 0.71292)
