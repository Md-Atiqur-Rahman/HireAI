

from src.Helper.extract_experience_details import check_experience_requirement, extract_experience_entries
from src.Helper.extract_skills import match_skills_grouped


def evaluate_requirement(req_text, resume_text, extracted_years=None):
    meets_experience, candidate_years, year_bounds = check_experience_requirement(req_text, resume_text, extracted_years)
    matched_keywords, missing_keywords = match_skills_grouped(req_text, resume_text)

    status = "✅ Match" if (meets_experience and matched_keywords) else "❌ Missing"
    score = round(len(matched_keywords) / (len(matched_keywords) + len(missing_keywords) + 1e-6), 2)

    if year_bounds[1]:
        exp_req = f"{year_bounds[0]}–{year_bounds[1]} years"
    elif year_bounds[0]:
        exp_req = f"{year_bounds[0]}+ years"
    else:
        exp_req = "Not specified"

    return {
        "requirement": req_text,
        "status": status,
        "score": score,
        "experience_check": f"Requirement: {exp_req}, Candidate: {candidate_years} years",
        "matched": matched_keywords,
        "missing": missing_keywords
    }

# ---------- Step 3: Pipeline ----------
def evaluate_resume_against_requirements(resume_text, requirements):
    entries, extracted_years = extract_experience_entries(resume_text)
    results = []
    for req in requirements:
        results.append(evaluate_requirement(req, resume_text, extracted_years))
    return results