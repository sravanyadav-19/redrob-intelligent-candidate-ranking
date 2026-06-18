import sys
sys.path.insert(0, 'src')
from scorer import load_and_score

# Score ALL candidates, not just top 100
import json
from scorer import rank_candidates

with open('data/parsed_candidates.json', 'r') as f:
    parsed_list = json.load(f)
with open('data/semantic_scores.json', 'r') as f:
    semantic_scores = json.load(f)
with open('data/structured_features.json', 'r') as f:
    features_dict = json.load(f)
with open('data/behavioral_scores.json', 'r') as f:
    behavioral_dict = json.load(f)

print("Scoring all 100000 candidates...")
all_results = rank_candidates(
    parsed_list=parsed_list,
    semantic_scores=semantic_scores,
    features_dict=features_dict,
    behavioral_dict=behavioral_dict,
    top_n=100000   # get ALL ranked
)

# Find CAND_0000031 position
target_id = 'CAND_0000031'
target_idx = None
for i, r in enumerate(all_results):
    if r['candidate_id'] == target_id:
        target_idx = i
        break

print(f"\n{'Rank':<6} {'Candidate ID':<15} {'Score':<8} {'Semantic':<10} {'Systems':<10} {'Behavior':<10}")
print("-" * 60)

if target_idx is not None:
    # Print 3 above, the target, 3 below
    start = max(0, target_idx - 3)
    end   = min(len(all_results), target_idx + 4)
    for r in all_results[start:end]:
        marker = " <-- TARGET" if r['candidate_id'] == target_id else ""
        print(f"{r['rank']:<6} {r['candidate_id']:<15} {r['final_score']:<8.4f} "
              f"{r['semantic_score']:<10.4f} {r['systems_built_score']:<10.4f} "
              f"{r['behavior_score']:<10.4f}{marker}")
else:
    print(f"{target_id} not found in results")

print()
print(f"Rank 100 cutoff score: {all_results[99]['final_score']}")
print(f"CAND_0000031 actual rank: {all_results[target_idx]['rank'] if target_idx is not None else 'N/A'}")
print(f"CAND_0000031 actual score: {all_results[target_idx]['final_score'] if target_idx is not None else 'N/A'}")
