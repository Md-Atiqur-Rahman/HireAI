import sys
import os



# Add the project root to PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

import re
import spacy
from sentence_transformers import SentenceTransformer, util
import torch

from src.feature.helper_requirement_analyzer.check_exp_ok import check_exp_ok_or_not_ok
from src.feature.helper_requirement_analyzer.check_experience_skills import check_experience_skills
from src.feature.helper_requirement_analyzer.check_technical_requirement import check_technical_requirement
from src.feature.helper_requirement_analyzer.summarize_results import summarize_results
from src.feature.helper_requirement_analyzer.check_education import check_education
# from src.Helper.resume_experience_gimini import generate_resume_experience_gemini
# from src.Helper.parser import extract_text_from_pdf
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
        # ---------- Experience ----------
        # Extract min/max years
        total_years,exp_ok = check_exp_ok_or_not_ok(requirement,resume_text)
        # Extract required skills from requirement (text after "in" or after years)
        check_experience_skills(resume_text,requirement,resume_keywords,total_years,exp_ok,category)

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
        check_technical_requirement(requirement, resume_text)
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
    matched_skills = [] 

    # iterate over each category
    for category, reqs in job_requirements.items():
        if not reqs:
            continue

        # যদি reqs string হয়, তাহলে list বানাব
        if isinstance(reqs, str):
            reqs = [reqs]

        for requirement in reqs:
            if not requirement.strip():
                continue
            check = check_requirement(requirement, resume_sentences, resume_keywords, resume_text, category)
            results.append(check)

            # Experience + TechnicalSkills থেকে matched skills collect করব
            if category.lower() in ["experience", "technicalskills"]:
                if "matched_keywords" in check:
                    matched_skills.extend(check["matched_keywords"])

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

    # শুধুমাত্র matched skills return
    return summary_text, total_experience, overall_score, list(set(matched_skills))
