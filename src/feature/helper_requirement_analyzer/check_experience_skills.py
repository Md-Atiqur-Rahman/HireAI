import os
import re
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sentence_transformers import SentenceTransformer, util
from src.feature.dataclasses.requirementresults import RequirementResult

sbert_model = SentenceTransformer("all-MiniLM-L6-v2")
import re
from src.feature.helper_requirement_analyzer.check_technical_requirement import split_skills_line
from src.feature.dataclasses.requirementresults import RequirementResult


def check_experience_skills(resume_text, requirement, resume_keywords, total_years, category,exp_ok,required_years):
    """
    Check both experience years and required technical skills for a requirement.
    Partial match: at least 50% of required skills must be matched.
    """

    # --- 1. Extract required skills from requirement text ---
    skills_part = re.split(r"experience in|with experience in|experience with", requirement, flags=re.IGNORECASE)[-1]
    required_skills = [s.strip() for s in re.split(r"[,/|]", skills_part) if s.strip()]
    resume_sentences = [s.strip() for s in resume_text.split("\n") if s.strip()]
    
    matched = []
    missing = []

    resume_skills_sentences = []
    for sent in resume_sentences:
        if "," in sent and len(sent.split()) < 20:  # heuristic: likely a skills list
            resume_skills_sentences.extend(split_skills_line(sent))
        else:
            resume_skills_sentences.append(sent)
    # --- 2. Match skills ---
    for skill in required_skills:
        found = False

        # Direct mention in resume text
        if re.search(rf"\b{re.escape(skill)}\b", resume_text, re.IGNORECASE):
            matched.append(skill)
            found = True
        if not found:
            # Fallback to keyword bag
            for kw in resume_skills_sentences:
                if skill.lower() in kw.lower():
                    matched.append(skill)
                    found = True
                    break
        # --- 3. Fallback: semantic similarity (SBERT) ---
        if not found and len(skill.split()) > 1 and resume_skills_sentences:
            resume_embs = sbert_model.encode(resume_skills_sentences, convert_to_tensor=True)
            req_emb = sbert_model.encode(skill, convert_to_tensor=True)
            sims = util.cos_sim(req_emb, resume_embs)[0]
            test = float(sims.max())
            if float(sims.max()) >= 0.5:  # semantic threshold
                matched.append(skill)
                found = True
        if not found:
            missing.append(skill)

    # --- 3. Calculate skill match ratio ---
    skills_ratio = len(matched) / len(required_skills) if required_skills else 0
    skills_ok = skills_ratio >= 0.5  # ✅ at least 50% match

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
                reason = f"User has {total_years} years, requires {required_years}"
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
