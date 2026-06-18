"""
rank.py — Single command entry point for submission reproduction.

Usage:
    python rank.py --candidates ./candidates.jsonl --out ./submission.csv

Constraints satisfied:
    - Runs in < 5 minutes on CPU
    - No network calls during inference
    - No GPU required
    - 16GB RAM sufficient
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from pipeline import run_pipeline


def main():
    parser = argparse.ArgumentParser(
        description="Redrob Intelligent Candidate Ranking — Team: just_started"
    )
    parser.add_argument(
        "--candidates",
        type=str,
        default="data/raw/candidates.jsonl",
        help="Path to candidates.jsonl file"
    )
    parser.add_argument(
        "--out",
        type=str,
        default="output/just_started.csv",
        help="Path for output CSV file"
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=100,
        help="Number of top candidates to rank (default: 100)"
    )
    args = parser.parse_args()

    print("=" * 60)
    print("  Redrob Intelligent Candidate Ranking")
    print("  Team: just_started")
    print("=" * 60)

    run_pipeline(
        candidates_path = args.candidates,
        output_path     = args.out,
        top_n           = args.top_n,
    )


if __name__ == "__main__":
    main()
