"""
Module: Candidate Profile Parser
Owner: Ganesh
Branch: feature/ganesh-embedder
Input: data/raw/candidates.jsonl
Output: data/parsed_candidates.json
"""

import json
from pathlib import Path


CONSULTING_FIRMS = {
    "tcs", "tata consultancy", "infosys", "wipro", "accenture",
    "cognizant", "capgemini", "hcl", "tech mahindra", "mphasis",
    "hexaware", "mindtree", "ltimindtree", "persistent", "niit"
}


def is_consulting(company_name: str) -> bool:
    name = company_name.lower().strip()
    return any(firm in name for firm in CONSULTING_FIRMS)


def safe_str(val) -> str:
    if val is None:
        return ""
    return str(val).strip()


def safe_float(val, default=0.0) -> float:
    try:
        return float(val)
    except (TypeError, ValueError):
        return default


def parse_candidate(raw: dict) -> dict:
    """
    Parse one raw candidate record into a clean flat dict.
    Never crashes — all missing fields get safe defaults.
    """

    cid = safe_str(raw.get("candidate_id"))

    # ── Profile ──────────────────────────────────────────────────────────
    profile = raw.get("profile") or {}
    name           = safe_str(profile.get("anonymized_name"))
    headline       = safe_str(profile.get("headline"))
    summary        = safe_str(profile.get("summary"))
    location       = safe_str(profile.get("location"))
    country        = safe_str(profile.get("country"))
    years_exp      = safe_float(profile.get("years_of_experience"))
    current_title  = safe_str(profile.get("current_title"))
    current_company= safe_str(profile.get("current_company"))
    industry       = safe_str(profile.get("current_industry"))

    # ── Career history ────────────────────────────────────────────────────
    career         = raw.get("career_history") or []
    all_companies  = [safe_str(j.get("company")) for j in career]
    all_titles     = [safe_str(j.get("title")) for j in career]

    # Full experience text for embedding and feature extraction
    exp_texts = []
    for job in career:
        title   = safe_str(job.get("title"))
        company = safe_str(job.get("company"))
        desc    = safe_str(job.get("description"))
        dur     = safe_float(job.get("duration_months"))
        exp_texts.append(f"{title} at {company} ({dur:.0f} months): {desc}")
    experience_text = " | ".join(exp_texts)

    # Consulting-only flag
    if all_companies:
        consulting_only = all(is_consulting(c) for c in all_companies)
    else:
        consulting_only = False

    # Has at least one product company
    has_product_company = any(not is_consulting(c) for c in all_companies)

    # Title chasing: avg tenure < 12 months AND 4+ companies
    # AND no upward career progression in title seniority
    # A genuine ML career across product companies is NOT title chasing
    NONTECHNICAL_HOPS = {
        "marketing", "sales", "hr", "accountant", "operations",
        "content", "graphic", "civil", "mechanical", "customer support"
    }
    if len(career) >= 4:
        durations = [safe_float(j.get("duration_months")) for j in career]
        avg_tenure = sum(durations) / len(durations)
        all_titles_lower = " ".join(all_titles).lower()
        is_nontechnical_hopper = any(
            t in all_titles_lower for t in NONTECHNICAL_HOPS
        )
        title_chasing = avg_tenure < 12.0 and is_nontechnical_hopper
    else:
        title_chasing = False

    # ── Skills ────────────────────────────────────────────────────────────
    skills_raw = raw.get("skills") or []
    skills_text = " ".join([safe_str(s.get("name")) for s in skills_raw])

    skill_list = []
    for s in skills_raw:
        skill_list.append({
            "name":         safe_str(s.get("name")),
            "proficiency":  safe_str(s.get("proficiency")),
            "endorsements": int(safe_float(s.get("endorsements"))),
            "duration_months": int(safe_float(s.get("duration_months")))
        })

    # ── Honeypot detection ────────────────────────────────────────────────
    # Flag 1: expert skill with 0 months duration
    honeypot_skill = any(
        s["proficiency"] == "expert" and s["duration_months"] == 0
        for s in skill_list
    )

    # Flag 2: years_of_experience vs sum of career durations
    total_career_months = sum(safe_float(j.get("duration_months")) for j in career)
    stated_months = years_exp * 12
    # If stated experience is more than 3 years greater than career history
    exp_gap = stated_months - total_career_months
    honeypot_exp = exp_gap > 36  # 3 year gap is suspicious

    is_honeypot = honeypot_skill or honeypot_exp

    # ── Education ─────────────────────────────────────────────────────────
    education = raw.get("education") or []
    edu_text = " ".join([
        f"{safe_str(e.get('degree'))} {safe_str(e.get('field_of_study'))} {safe_str(e.get('institution'))}"
        for e in education
    ])
    edu_tier = "unknown"
    if education:
        # Take the best tier
        tiers = [safe_str(e.get("tier", "unknown")) for e in education]
        tier_order = {"tier_1": 0, "tier_2": 1, "tier_3": 2, "tier_4": 3, "unknown": 4}
        tiers_sorted = sorted(tiers, key=lambda t: tier_order.get(t, 4))
        edu_tier = tiers_sorted[0]

    # ── Redrob signals ────────────────────────────────────────────────────
    rs = raw.get("redrob_signals") or {}

    last_active      = safe_str(rs.get("last_active_date"))
    open_to_work     = bool(rs.get("open_to_work_flag", False))
    response_rate    = safe_float(rs.get("recruiter_response_rate"), 0.3)
    notice_days      = int(safe_float(rs.get("notice_period_days"), 60))
    profile_complete = safe_float(rs.get("profile_completeness_score"), 50.0)
    github_score     = safe_float(rs.get("github_activity_score"), -1)
    if github_score < 0:
        github_score = 0.0  # treat -1 as null → 0

    offer_rate       = safe_float(rs.get("offer_acceptance_rate"), -1)
    if offer_rate < 0:
        offer_rate = None  # exclude from scoring

    interview_rate   = safe_float(rs.get("interview_completion_rate"), 0.5)
    willing_relocate = bool(rs.get("willing_to_relocate", False))
    country_val      = country.strip().lower()

    # Location eligibility (JD is India-based)
    india_locations = {"india"}
    is_india_based = country_val == "india"
    location_eligible = is_india_based or willing_relocate

    # Salary range — handle inverted min/max
    salary = rs.get("expected_salary_range_inr_lpa") or {}
    sal_min = safe_float(salary.get("min"), 0)
    sal_max = safe_float(salary.get("max"), 0)
    if sal_min > sal_max and sal_max > 0:
        sal_min, sal_max = sal_max, sal_min  # fix inverted

    # Skill assessment scores (sparse dict)
    assessment_scores = rs.get("skill_assessment_scores") or {}
    avg_assessment = 0.0
    if assessment_scores:
        scores = [v for v in assessment_scores.values() if isinstance(v, (int, float))]
        if scores:
            avg_assessment = sum(scores) / len(scores)

    # ── Combined text blob for embedding ─────────────────────────────────
    # Weight: experience descriptions > title > skills > summary
    text_blob = " ".join(filter(None, [
        current_title,
        experience_text,
        skills_text,
        summary,
        edu_text,
    ]))

    return {
        "candidate_id":       cid,
        "name":               name,
        "headline":           headline,
        "summary":            summary,
        "country":            country,
        "location":           location,
        "years_exp":          years_exp,
        "current_title":      current_title,
        "current_company":    current_company,
        "industry":           industry,
        "experience_text":    experience_text,
        "skills_text":        skills_text,
        "skill_list":         skill_list,
        "all_companies":      all_companies,
        "all_titles":         all_titles,
        "consulting_only":    consulting_only,
        "has_product_company":has_product_company,
        "title_chasing":      title_chasing,
        "is_honeypot":        is_honeypot,
        "edu_tier":           edu_tier,
        "edu_text":           edu_text,
        "last_active_date":   last_active,
        "open_to_work":       open_to_work,
        "response_rate":      response_rate,
        "notice_days":        notice_days,
        "profile_completeness": profile_complete,
        "github_score":       github_score,
        "interview_rate":     interview_rate,
        "willing_relocate":   willing_relocate,
        "location_eligible":  location_eligible,
        "avg_assessment":     avg_assessment,
        "sal_min":            sal_min,
        "sal_max":            sal_max,
        "text_blob":          text_blob,
    }


def parse_all(input_path: str, output_path: str):
    """
    Read candidates.jsonl, parse all, save to parsed_candidates.json
    """
    input_path  = Path(input_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Reading: {input_path}")
    parsed = []
    with open(input_path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            try:
                raw = json.loads(line)
                parsed.append(parse_candidate(raw))
            except Exception as e:
                print(f"  Warning: skipped line {i+1} — {e}")

    print(f"Parsed {len(parsed)} candidates.")

    honeypots = sum(1 for c in parsed if c["is_honeypot"])
    print(f"Detected {honeypots} likely honeypot candidates.")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(parsed, f)

    print(f"Saved: {output_path}")
    return parsed


if __name__ == "__main__":
    parse_all(
        input_path="data/raw/candidates.jsonl",
        output_path="data/parsed_candidates.json"
    )
