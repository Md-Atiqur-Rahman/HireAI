import re
import spacy
from sentence_transformers import SentenceTransformer, util
import torch

from src.feature.helper_requirement_analyzer.summarize_results import summarize_results
from src.feature.helper_requirement_analyzer.extract_experience import extract_experience_entries, extract_years_from_text
from src.feature.helper_requirement_analyzer.check_education import check_education
from src.Helper.resume_experience_gimini import generate_resume_experience_gemini
from src.Helper.parser import extract_text_from_pdf
# ===============================
# Load Models
# ===============================
nlp = spacy.load("en_core_web_sm")
sbert_model = SentenceTransformer("all-MiniLM-L6-v2")


# ===============================
# Keyword Extractor
# ===============================
def extract_keywords(text):
    doc = nlp(text.lower())
    return {token.lemma_ for token in doc if token.pos_ in ["NOUN", "PROPN", "VERB"]}


def check_requirement(requirement, resume_sentences, resume_keywords, resume_text, category="Other"):
    """
    Enhanced requirement checker:
    - For Experience: validates years + skills (both must match)
    - Skills must meet >=50% semantic match
    - For TechnicalSkills: same semantic threshold
    - For others: SBERT + keyword match
    """
    # ---------- EXPERIENCE ----------
    if category.lower() == "experience" or "year" in requirement.lower():
        # Extract min/max years
        range_match = re.search(r"(\d+)\s*-\s*(\d+)\s*years", requirement, re.IGNORECASE)
        single_match = re.search(r"(\d+)\+?\s*years", requirement, re.IGNORECASE)

        min_years, max_years = None, None
        if range_match:
            min_years, max_years = int(range_match.group(1)), int(range_match.group(2))
        elif single_match:
            min_years = int(single_match.group(1))

        # Extract total years from resume
        _, total_years = extract_experience_entries(resume_text)
        if total_years == 0:
            total_years = extract_years_from_text(resume_text)

        # Check years
        exp_ok = False
        if min_years is not None and max_years is not None:
            exp_ok = min_years <= total_years <= max_years
        elif min_years is not None:
            exp_ok = total_years >= min_years

        # Extract required skills from requirement (text after "in" or after years)
        skills_part = re.split(r"experience in|with experience in|experience with", requirement, flags=re.IGNORECASE)[-1]
        required_skills = [s.strip() for s in re.split(r"[,/|]", skills_part) if s.strip()]

        # Check skills with SBERT similarity
        matched, missing = [], []
        skills_ok = True
        if required_skills:
            req_embs = sbert_model.encode(required_skills, convert_to_tensor=True)
            cand_embs = sbert_model.encode(list(resume_keywords), convert_to_tensor=True)
            for i, req in enumerate(required_skills):
                sims = util.cos_sim(req_embs[i], cand_embs)[0]
                if float(sims.max()) >= 0.6:
                    matched.append(req)
                else:
                    missing.append(req)
            skills_ok = len(matched) / len(required_skills) >= 0.5

        # Final status: only if BOTH experience and skills are ok
        status = "✅ Match" if exp_ok and skills_ok else "❌ Missing"

        # Build reason string
        if not exp_ok and not skills_ok:
            reason = f"User has {total_years} years and no {', '.join(missing)} mentioned"
        elif not exp_ok:
            reason = f"User has {total_years} years"
        elif not skills_ok:
            reason = f"User has {total_years} years and no {', '.join(missing)} mentioned"
        else:
            reason = f"User has {total_years} years"

        return {
            "requirement": requirement,
            "status": status,
            "experience_check": reason,
            "matched_keywords": matched,
            "missing_keywords": missing,
            "exp_ok": exp_ok,
            "skills_ok": skills_ok,
            "category": category
        }
    # ---------- EDUCATION ----------
    if category.lower() == "education":
        status, reason = check_education(resume_text, requirement)
        return {
            "requirement": requirement,
            "status": status,
            "reason": reason,
            "category": category
        }
    # ---------- TECHNICAL SKILLS ----------
    if category.lower() == "technicalskills":
        required_skills = [s.strip() for s in re.split(r"[,/|]", requirement) if s.strip()]
        candidate_skills = list(resume_keywords)

        req_embs = sbert_model.encode(required_skills, convert_to_tensor=True)
        cand_embs = sbert_model.encode(candidate_skills, convert_to_tensor=True)

        matched, missing = [], []
        for i, req in enumerate(required_skills):
            sims = util.cos_sim(req_embs[i], cand_embs)[0]
            if float(sims.max()) >= 0.6:  # semantic threshold
                matched.append(req)
            else:
                missing.append(req)

        ratio = len(matched) / len(required_skills) if required_skills else 0
        status = "✅ Match" if ratio >= 0.5 else "❌ Missing"

        return {
            "requirement": requirement,
            "status": status,
            "category": category,
            "matched_keywords": matched,
            "missing_keywords": missing
        }

    # ---------- GENERIC REQUIREMENTS ----------
    req_emb = sbert_model.encode(requirement, convert_to_tensor=True)
    res_embs = sbert_model.encode(resume_sentences, convert_to_tensor=True)
    sims = util.cos_sim(req_emb, res_embs)[0]
    best_score = float(torch.max(sims)) if len(sims) > 0 else 0

    req_keywords = extract_keywords(requirement)
    matched = req_keywords & resume_keywords
    missing = req_keywords - resume_keywords

    return {
        "requirement": requirement,
        "status": "✅ Match" if best_score >= 0.5 else "❌ Missing",
        "score": round(best_score, 2),
        "category": category,
        "matched_keywords": list(matched),
        "missing_keywords": list(missing)
    }

def evaluate_resume(resume_text, job_requirements):
    resume_sentences = [s.strip() for s in resume_text.split("\n") if s.strip()]
    resume_keywords = extract_keywords(resume_text)

    results = []

    # iterate over each category
    for category, reqs in job_requirements.items():
        if not reqs:
            continue

        # if reqs is a single string → wrap in list
        if isinstance(reqs, str):
            reqs = [reqs]

        for requirement in reqs:
            if not requirement.strip():
                continue
            check = check_requirement(requirement, resume_sentences, resume_keywords, resume_text, category)
            results.append(check)

    # --- summarization ---
    overall_score, summary_text = summarize_results(results)

    # --- total experience extraction ---
    total_experience = 0.0
    for r in results:
        if r["category"].lower() == "experience" and "experience_check" in r:
            match = re.search(r"(\d+(\.\d+)?)\s*years", r["experience_check"])
            if match:
                total_experience = float(match.group(1))
                break

    return summary_text, total_experience, overall_score

