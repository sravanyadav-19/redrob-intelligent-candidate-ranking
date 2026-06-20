"""
Module: Submission Format Validator Tests
Owner: Sahitya
Branch: feature/sahitya-behavioral
Purpose: Verify that the submission CSV passes all validator rules.
         Also tests edge cases: duplicate ranks, wrong column order,
         non-increasing scores, tie-break violations.

Run from project root:
    python tests/test_validator.py
"""

import csv
import sys
import os
from pathlib import Path

# Add root to path so validate_submission can be imported
sys.path.insert(0, str(Path(__file__).parent.parent))
from validate_submission import validate_submission


def write_csv(path: str, rows: list, header: list = None):
    """Helper to write a test CSV file."""
    if header is None:
        header = ["candidate_id", "rank", "score", "reasoning"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)


def make_valid_rows(n: int = 100) -> list:
    """Generate n valid rows with non-increasing scores."""
    rows = []
    for i in range(1, n + 1):
        score = round(1.0 - (i - 1) * 0.005, 4)
        rows.append([
            f"CAND_{i:07d}",
            str(i),
            str(score),
            f"Test candidate {i} reasoning string."
        ])
    return rows


# ── Test functions ────────────────────────────────────────────────────────────

def test_valid_submission():
    """A perfectly valid submission should pass with no errors."""
    path = "tests/temp_valid.csv"
    write_csv(path, make_valid_rows(100))
    errors = validate_submission(path)
    os.remove(path)
    assert errors == [], f"Valid submission failed: {errors}"
    print("  PASS  test_valid_submission")


def test_wrong_column_order():
    """Wrong column order should fail."""
    path = "tests/temp_col_order.csv"
    write_csv(path, make_valid_rows(100),
              header=["rank", "candidate_id", "score", "reasoning"])
    errors = validate_submission(path)
    os.remove(path)
    assert any("header" in e.lower() for e in errors), \
        "Should fail on wrong column order"
    print("  PASS  test_wrong_column_order")


def test_wrong_row_count():
    """99 rows instead of 100 should fail."""
    path = "tests/temp_99rows.csv"
    write_csv(path, make_valid_rows(99))
    errors = validate_submission(path)
    os.remove(path)
    assert any("99" in e or "100" in e for e in errors), \
        "Should fail on wrong row count"
    print("  PASS  test_wrong_row_count")


def test_duplicate_rank():
    """Duplicate rank should fail."""
    path = "tests/temp_dup_rank.csv"
    rows = make_valid_rows(100)
    rows[1][1] = "1"   # rank 2 → set to 1 (duplicate)
    write_csv(path, rows)
    errors = validate_submission(path)
    os.remove(path)
    assert any("duplicate" in e.lower() for e in errors), \
        "Should fail on duplicate rank"
    print("  PASS  test_duplicate_rank")


def test_duplicate_candidate_id():
    """Duplicate candidate_id should fail."""
    path = "tests/temp_dup_cid.csv"
    rows = make_valid_rows(100)
    rows[1][0] = rows[0][0]   # make row 2 same ID as row 1
    write_csv(path, rows)
    errors = validate_submission(path)
    os.remove(path)
    assert any("duplicate" in e.lower() for e in errors), \
        "Should fail on duplicate candidate_id"
    print("  PASS  test_duplicate_candidate_id")


def test_score_increasing():
    """Scores that increase with rank should fail."""
    path = "tests/temp_increasing.csv"
    rows = make_valid_rows(100)
    rows[5][2] = "0.999"   # rank 6 score higher than rank 5
    write_csv(path, rows)
    errors = validate_submission(path)
    os.remove(path)
    assert any("non-increasing" in e.lower() or
               "score" in e.lower() for e in errors), \
        "Should fail on increasing scores"
    print("  PASS  test_score_increasing")


def test_invalid_candidate_id_format():
    """Wrong candidate_id format should fail."""
    path = "tests/temp_bad_cid.csv"
    rows = make_valid_rows(100)
    rows[0][0] = "CANDIDATE_001"   # wrong format
    write_csv(path, rows)
    errors = validate_submission(path)
    os.remove(path)
    assert any("CAND_" in e or "7 digits" in e.lower() or
               "candidate_id" in e.lower() for e in errors), \
        "Should fail on invalid candidate_id format"
    print("  PASS  test_invalid_candidate_id_format")


def test_rank_out_of_range():
    """Rank 0 or rank 101 should fail."""
    path = "tests/temp_bad_rank.csv"
    rows = make_valid_rows(100)
    rows[0][1] = "0"   # rank 0 is invalid
    write_csv(path, rows)
    errors = validate_submission(path)
    os.remove(path)
    assert any("rank" in e.lower() for e in errors), \
        "Should fail on rank out of range"
    print("  PASS  test_rank_out_of_range")


def test_actual_submission_file():
    """Test the actual submission file if it exists."""
    submission_path = "output/just_started.csv"
    if not Path(submission_path).exists():
        print("  SKIP  test_actual_submission_file (file not found)")
        return
    errors = validate_submission(submission_path)
    assert errors == [], f"Actual submission failed validation: {errors}"
    print("  PASS  test_actual_submission_file")


# ── Run all tests ─────────────────────────────────────────────────────────────

def run_all():
    print("\nRunning submission validator tests...\n")

    tests = [
        test_valid_submission,
        test_wrong_column_order,
        test_wrong_row_count,
        test_duplicate_rank,
        test_duplicate_candidate_id,
        test_score_increasing,
        test_invalid_candidate_id_format,
        test_rank_out_of_range,
        test_actual_submission_file,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"  FAIL  {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"  ERROR {test.__name__}: {e}")
            failed += 1

    print(f"\nResults: {passed} passed, {failed} failed out of {len(tests)} tests")

    if failed == 0:
        print("All tests passed. ✅")
    else:
        print("Some tests failed. ❌")
        sys.exit(1)


if __name__ == "__main__":
    run_all()
