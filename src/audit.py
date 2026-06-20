"""
Module: Data Audit
Owner: Rajesh
Branch: feature/rajesh-feature-extractor
Purpose: Scan candidates.jsonl and report dataset statistics,
         null/missing field counts, and distribution insights.
Input: data/raw/candidates.jsonl
Output: printed report + data/audit_report.txt
"""

import json
from pathlib import Path
from collections import Counter
from datetime import datetime


def audit(input_path: str = "data/raw/candidates.jsonl",
          output_path: str = "data/audit_report.txt"):

    input_path  = Path(input_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    lines = []
    total = 0
    null_summary       = 0
    null_skills        = 0
    null_redrob        = 0
    null_experience    = 0
    null_education     = 0
    no_github          = 0
    open_to_work       = 0
    willing_relocate   = 0
    country_counter    = Counter()
    industry_counter   = Counter()
    experience_buckets = Counter()
    honeypot_count     = 0

    CONSULTING = {
        "tcs", "tata consultancy", "infosys", "wipro", "accenture",
        "cognizant", "capgemini", "hcl", "tech mahindra", "mphasis",
        "hexaware", "mindtree"
    }

    print(f"Reading: {input_path}")

    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                c = json.loads(line)
            except Exception:
                continue

            total += 1
            profile  = c.get("profile") or {}
            rs       = c.get("redrob_signals") or {}
            career   = c.get("career_history") or []
            skills   = c.get("skills") or []
            edu      = c.get("education") or []

            # Null checks
            if not profile.get("summary", "").strip():
                null_summary += 1
            if not skills:
                null_skills += 1
            if not rs:
                null_redrob += 1
            if not career:
                null_experience += 1
            if not edu:
                null_education += 1

            # Redrob signals
            if rs.get("github_activity_score", -1) == -1:
                no_github += 1
            if rs.get("open_to_work_flag"):
                open_to_work += 1
            if rs.get("willing_to_relocate"):
                willing_relocate += 1

            # Country distribution
            country = profile.get("country", "Unknown")
            country_counter[country] += 1

            # Industry distribution
            industry = profile.get("current_industry", "Unknown")
            industry_counter[industry] += 1

            # Experience buckets
            yrs = float(profile.get("years_of_experience") or 0)
            if yrs < 2:
                experience_buckets["0-2 yrs"] += 1
            elif yrs < 5:
                experience_buckets["2-5 yrs"] += 1
            elif yrs < 9:
                experience_buckets["5-9 yrs (JD sweet spot)"] += 1
            elif yrs < 13:
                experience_buckets["9-13 yrs"] += 1
            else:
                experience_buckets["13+ yrs"] += 1

            # Honeypot: expert skill with 0 months
            honeypot_skill = any(
                s.get("proficiency") == "expert" and
                int(s.get("duration_months") or 0) == 0
                for s in skills
            )
            # Honeypot: experience gap > 3 years
            total_months = sum(
                int(j.get("duration_months") or 0) for j in career
            )
            stated_months = yrs * 12
            honeypot_exp = (stated_months - total_months) > 36

            if honeypot_skill or honeypot_exp:
                honeypot_count += 1

    # Build report
    report = []
    report.append("=" * 55)
    report.append("  REDROB DATASET AUDIT REPORT")
    report.append(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append("=" * 55)
    report.append("")
    report.append(f"Total candidates:          {total:,}")
    report.append("")
    report.append("── NULL / MISSING FIELDS ──────────────────────────")
    report.append(f"  Missing summary:          {null_summary:,} ({null_summary/total*100:.1f}%)")
    report.append(f"  Missing skills:           {null_skills:,} ({null_skills/total*100:.1f}%)")
    report.append(f"  Missing career history:   {null_experience:,} ({null_experience/total*100:.1f}%)")
    report.append(f"  Missing education:        {null_education:,} ({null_education/total*100:.1f}%)")
    report.append(f"  Missing redrob signals:   {null_redrob:,} ({null_redrob/total*100:.1f}%)")
    report.append(f"  No GitHub linked:         {no_github:,} ({no_github/total*100:.1f}%)")
    report.append("")
    report.append("── BEHAVIORAL SIGNALS ─────────────────────────────")
    report.append(f"  Open to work:             {open_to_work:,} ({open_to_work/total*100:.1f}%)")
    report.append(f"  Willing to relocate:      {willing_relocate:,} ({willing_relocate/total*100:.1f}%)")
    report.append("")
    report.append("── HONEYPOT DETECTION ─────────────────────────────")
    report.append(f"  Suspected honeypots:      {honeypot_count:,} ({honeypot_count/total*100:.1f}%)")
    report.append("")
    report.append("── EXPERIENCE DISTRIBUTION ────────────────────────")
    for bucket, count in sorted(experience_buckets.items()):
        report.append(f"  {bucket:<30} {count:,}")
    report.append("")
    report.append("── TOP 10 COUNTRIES ───────────────────────────────")
    for country, count in country_counter.most_common(10):
        report.append(f"  {country:<30} {count:,}")
    report.append("")
    report.append("── TOP 10 INDUSTRIES ──────────────────────────────")
    for industry, count in industry_counter.most_common(10):
        report.append(f"  {industry:<30} {count:,}")
    report.append("")
    report.append("=" * 55)

    full_report = "\n".join(report)
    print(full_report)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_report)

    print(f"\nSaved: {output_path}")


if __name__ == "__main__":
    audit()
