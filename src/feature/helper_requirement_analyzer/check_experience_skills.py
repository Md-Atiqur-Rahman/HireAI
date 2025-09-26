import re
from src.feature.dataclasses.requirementresults import RequirementResult


def check_experience_skills(resume_text, requirement, resume_keywords, total_years, category):
    """
    Check both experience years and required technical skills for a requirement.
    Partial match: at least 50% of required skills must be matched.
    """

    # --- 1. Extract required skills from requirement text ---
    skills_part = re.split(r"experience in|with experience in|experience with", requirement, flags=re.IGNORECASE)[-1]
    required_skills = [s.strip() for s in re.split(r"[,/|]", skills_part) if s.strip()]

    matched = []
    missing = []

    # --- 2. Match skills ---
    for skill in required_skills:
        found = False

        # Direct mention in resume text
        if re.search(rf"\b{re.escape(skill)}\b", resume_text, re.IGNORECASE):
            matched.append(skill)
            found = True
        else:
            # Fallback to keyword bag
            for kw in resume_keywords:
                if skill.lower() in kw.lower():
                    matched.append(skill)
                    found = True
                    break

        if not found:
            missing.append(skill)

    # --- 3. Calculate skill match ratio ---
    skills_ratio = len(matched) / len(required_skills) if required_skills else 0
    skills_ok = skills_ratio >= 0.5  # ✅ at least 50% match

    # --- 4. Check experience years ---
    exp_ok = False
    required_years = None
    match = re.search(r"(\d+(\.\d+)?)\s*years", requirement, re.IGNORECASE)
    if match:
        required_years = float(match.group(1))
        exp_ok = total_years >= required_years
    else:
        exp_ok = True  # no years specified

    # --- 5. Build status & reason ---
    if exp_ok and skills_ok:
        status = "✅ Match"
        if missing:
            reason = f"User has {total_years} years, matched {len(matched)}/{len(required_skills)} skills (missing: {', '.join(missing)})"
        else:
            reason = f"User has {total_years} years and matched all skills"
    else:
        status = "❌ Missing"
        if not exp_ok:
            if required_years:
                reason = f"User has {total_years} years, requires {required_years} years"
            else:
                reason = "Experience not sufficient"
        elif not skills_ok:
            reason = f"User has {total_years} years but only matched {len(matched)}/{len(required_skills)} skills (missing: {', '.join(missing)})"
        else:
            reason = f"Does not meet requirement"

    # --- 6. Return result object ---
    return RequirementResult(
        requirement=requirement,
        status=status,
        score=0.0,
        experience_check=reason,
        reason =reason,
        exp_ok=exp_ok,
        skills_ok=skills_ok,
        total_years=total_years,
        category=category,
        matched_keywords=matched,
        missing_keywords=missing
    )
